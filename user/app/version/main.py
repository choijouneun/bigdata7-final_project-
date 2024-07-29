import time, sys
sys.path.append('/app/version')
from .preprocess.preprocessing import preprocess_main
from .data import *
from .config import BUCKET_SETTING


def main(subject):
    start_time = time.time()

    preprocess_main()  # pdf 전처리(수학만)

    # AWS 자격 증명 및 버킷 정보 설정
    bucket_name = BUCKET_SETTING['bucket_name']
    region = BUCKET_SETTING['region']
    prefix = f"workbook/{subject}/"

    setup_s3(bucket_name, region)  # s3 경로 설정
    upload_files(bucket_name)  # s3에 업로드
    
    s3_loader = S3DataLoader(bucket_name, prefix)
    es_manager = ElasticManager()
    db_manager = MariaDBManager()

    index_name, text_table_name, sim_table_name = get_table_names(subject)

    img_key_list, text_key_list = get_s3_keys(s3_loader)
    
    img_df = process_images(img_key_list, subject)  # 이미지 데이터 전처리
    text_df = process_texts(s3_loader, text_key_list, subject)  # 텍스트 데이터 전처리

    upload_questions_data(db_manager, text_table_name, text_df)  # 문항 테이블 Mariadb에 업로드
    
    merged_df = merge_dataframes(img_df, text_df, subject)  # 데이터 병합
    merged_df = process_merged_df(s3_loader, merged_df)  # 병합된 데이터 전처리
    
    upload_to_elasticsearch(es_manager, index_name, merged_df)  # 문항 테이블 Elasticsearch에 업로드

    upload_similarity_data(db_manager, index_name, sim_table_name, subject)

    end_time = time.time()
    return f"전체 실행 시간 : {end_time - start_time}"


def get_table_names(subject):
    if subject == 'KOR':
        return "questions_korean", "questions_korean", "similarity_korean"
    if subject == 'MATH':
        return "questions_math", "questions_math", "similarity_math"
    if subject == 'ENG':
        return "questions_english", "questions_english", "similarity_english"
    

# if __name__ == "__main__":
#     # print("과목을 선택하면 DB에 데이터를 넣을 수 있습니다.")
#     # print("1. 국어    2. 수학    3. 영어")
#     # choice = input("선택: ")

#     # if choice == '1':
#     #     subject = 'KOR'
#     # elif choice == '2':
#     #     subject = 'MATH'
#     # elif choice == '3':
#     #     subject = 'ENG'
#     # else:
#     #     print("잘못된 선택입니다.")
#     #     exit()

#     # main(subject)

#     if len(sys.argv) != 2:
#         print("Usage: python3 main.py <subject>")
#         sys.exit(1)
#     subject = sys.argv[1]
#     main(subject)