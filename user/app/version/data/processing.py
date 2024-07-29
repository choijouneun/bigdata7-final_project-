import re
import time
import pandas as pd
import numpy as np
import nltk
from nltk.corpus import stopwords
import sys
sys.path.append('/app/version')
from model.embedding import ImageEmbedding, TextEmbedding


def convert_subject_cat(subject, subject_cat):
    if subject == 'KOR':
        mapping = {
            'common': 1, 'speech_writing': 2, 'language_media': 3
        }
    elif subject == 'MATH':
        mapping = {
            'common': 1, 'A': 2, 'B': 3, 'statistics': 4, 'calculus': 5, 'geometry': 6
        }
    return mapping.get(subject_cat, 0)


def parse_key(subject, key):
    filename = key.split('/')[-1]
    match = re.match(r'KOR_G(\d)_(\d{4})_(\d{2})_((?:\w+_)+\w+)_(\d{2})\.png', filename) or \
            re.match(r'KOR_G(\d)_(\d{4})_(\d{2})_(\d{2})\.png', filename) or \
            re.match(r'MATH_G(\d)_(\d{4})_(\d{2})_(\w+?)_(\d{2})\.png', filename) or \
            re.match(r'MATH_G(\d)_(\d{4})_(\d{2})_(\d{2})\.png', filename) or \
            re.match(r'ENG_G(\d)_(\d{4})_(\d{2})_(\d{2})\.png', filename)
    
    if match:
        groups = match.groups()
        grade = int(groups[0])
        yyyy = int(groups[1])
        mm = int(groups[2])

        if subject == 'ENG':
            question_num = int(groups[3])
            subject_cat = 2 if question_num <= 17 else 1   # 17번까지 듣기(2). 18번부터 읽기(1)
        else:
            question_num = int(groups[4]) if len(groups) > 4 else int(groups[3])
            subject_cat = groups[3] if not groups[3].isdigit() else 'common'
            subject_cat = convert_subject_cat(subject, subject_cat)
            
        return {'grade': grade, 'yyyy': yyyy, 'mm': mm, 'subject_cat': subject_cat, 'question_num': question_num, 'image_key': key}

    return None

def parse_key_for_math_json(key):
    filename = key.split('/')[-1]
    match = re.match(r'MATH_G(\d)_(\d{4})_(\d{2})_(\w+)', filename) or \
            re.match(r'MATH_G(\d)_(\d{4})_(\d{2})', filename)

    if match:
        groups = match.groups()
        grade = int(groups[0])
        yyyy = int(groups[1])
        mm = int(groups[2])
        subject_cat = groups[3] if len(groups) == 4 else 'common'
        subject_cat_numeric = convert_subject_cat(subject_cat)
        return {'grade': grade, 'yyyy': yyyy, 'mm': mm, 'subject_cat': subject_cat_numeric}

    return None


def generate_pk(df):
    mm_str = f"{df['mm']:02d}"
    subject_cat_str = f"{df['subject_cat']:02d}"
    pk = f"G{df['grade']}{df['yyyy']}{mm_str}{subject_cat_str}Q{df['question_num']}"
    return pk


def process_images(img_key_list, subject):
    print('이미지 데이터프레임 생성 시작')
    data = []
    for key in img_key_list:
        parsed = parse_key(subject, key)
        if parsed:
            parsed['pk'] = generate_pk(parsed)
            data.append(parsed)
    img_df = pd.DataFrame(data, columns=['pk', 'grade', 'yyyy', 'mm', 'subject_cat', 'question_num', 'image_key'])
    print('이미지 데이터프레임 생성 완료')
    return img_df


def process_texts(s3_loader, text_key_list, subject):
    print('텍스트 데이터프레임 생성 시작')
    dfs = []
    if subject == 'MATH':
        for file in text_key_list:
            df = s3_loader.read_json_from_s3(file)
            # 파일명을 기반으로 subject_cat을 추출
            parsed_data = parse_key_for_math_json(file)
            if parsed_data:
                subject_cat_numeric = parsed_data['subject_cat']
                df['subject_cat'] = subject_cat_numeric  # JSON의 subject_cat을 대체
            dfs.append(df)
    else:
        for file in text_key_list:
            df = s3_loader.read_json_from_s3(file)
            dfs.append(df)

    text_df = pd.concat(dfs, ignore_index=True)
    
    for col in text_df.select_dtypes(include='float').columns:
        text_df[col] = text_df[col].astype('int')
        
    text_df['pk'] = text_df.apply(generate_pk, axis=1)
    text_df = text_df.drop_duplicates(subset='pk', keep='first')
    text_df = text_df.fillna('')

    if subject == 'MATH':
        text_df.rename(columns={'point':'points'}, inplace=True)
        
    columns_order = ['pk', 'grade', 'yyyy', 'mm', 'host', 'subject_cat', 'question_cat', 'question_num', 'points', 'text_title', 'text', 'text_yn', 'question', 'paragraph', 'choice1', 'choice2', 'choice3', 'choice4', 'choice5', 'short_answer', 'multiple_answer', 'text_exp', 'question_exp']

    for column in columns_order:
        if not column in text_df.columns:
            text_df[column] = ""
            
    text_df = text_df[columns_order]
    print('텍스트 데이터프레임 생성 완료')
    return text_df

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
def remove_stopwords(text):
    tokens = text.split()
    filtered_tokens = [word for word in tokens if word.lower() not in stop_words]
    return ' '.join(filtered_tokens)


def combine_columns(row, columns, subject):
    combined_text = ' '.join(row[col] for col in columns if pd.notnull(row[col]))
    if subject == "ENG":
        return remove_stopwords(combined_text)  # 불용어 제거
    else:
        return combined_text


def merge_dataframes(img_df, text_df, subject):
    columns_to_use = ['text', 'text_title', 'question', 'paragraph', 'choice1', 'choice2', 'choice3', 'choice4', 'choice5']
    text_df['combined_text'] = text_df.apply(lambda row: combine_columns(row, columns_to_use, subject), axis=1)

    # pk 기준으로 데이터프레임 합치기
    text_df_to_merge = text_df.drop(columns=['grade', 'yyyy', 'mm', 'subject_cat', 'question_num'])
    merged_df = pd.merge(img_df, text_df_to_merge, on='pk', how='left')
    print('병합된 데이터프레임 생성됨')
    return merged_df


def process_merged_df(s3_loader, merged_df):
    print('merged_df 이미지 임베딩 시작')
    img_start_time = time.time()
    # 이미지 임베딩 생성
    image_embedder = ImageEmbedding()
    img_features = []
    for file in merged_df['image_key']:
        try:
            img = s3_loader.read_image_from_s3(file)
            features = image_embedder.get_image_embedding(img)
            img_features.append(features)
        except Exception as e:
            print('예외가 발생했습니다.', e)
            img_features.append(None)
    merged_df['image_vec'] = img_features
    img_end_time = time.time()
    print("걸린 시간 : ", img_end_time - img_start_time)
    
    print('merged_df 텍스트 임베딩 시작')
    text_start_time = time.time()
    # 텍스트 임베딩 생성
    text_embedder = TextEmbedding()
    texts = merged_df['combined_text'].tolist()
    texts = [str(text) for text in texts]
    text_features = text_embedder.embed_texts(texts)
    merged_df['text_vec'] = text_features.tolist()
    text_end_time = time.time()
    print("걸린 시간 : ", text_end_time - text_start_time)
    print('merged_df 임베딩 완료')

    # 768차원의 0.5로 채워진 벡터 생성
    half_vector = np.full(768, 0.5)
    
    # NaN 값을 768차원의 0.5 벡터로 대체
    merged_df['text_vec'] = merged_df['text_vec'].apply(lambda x: half_vector if isinstance(x, float) and np.isnan(x) else x)
    
    # 데이터 타입 변환 및 NaN 값 처리
    for col in merged_df.columns:
        type = merged_df[col].dtype
        if type == 'object':
            merged_df[col] = merged_df[col].fillna("")
        else:
            merged_df[col] = merged_df[col].fillna(0)
            if type == 'float64':
                merged_df[col] = merged_df[col].astype('int64')

    # 컬럼 순서 조정
    columns_order = ['pk', 'grade', 'yyyy', 'mm', 'host', 'subject_cat', 'question_cat', 'question_num', 'points', 'text_title', 'text', 'text_yn', 'question', 'paragraph', 'choice1', 'choice2', 'choice3', 'choice4', 'choice5', 'short_answer', 'multiple_answer', 'text_exp', 'question_exp', 'text_vec', 'image_key', 'image_vec']
    merged_df = merged_df[columns_order]
    
    return merged_df
