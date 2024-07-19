import re
import pandas as pd
import os

class BaseProcessor:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory

    def clean_question_text(self, question):
        # 불필요한 문자와 문자열 제거
        question = re.sub(r"\n|\\|plaintext|markdown|=|:|-|\*", " ", question)
        question = re.sub(r"다음은 추출된 보기 부분입니다|아래는 보기만 추출한 것입니다|"
                          r"보기만 추출해드리면 다음과 같습니다|좋습니다. 다음과 같이 보기를 추출할 수 있습니다|"
                          r"보기만 추출했어|다음은 예시에서 추출한 보기들입니다|"
                          r"당신이 예시로 준 '보기' 부분을 추출한 것처럼, 주어진 문제에서 보기 부분을 다음과 같이 추출할 수 있습니다|"
                          r"예시를 참고하여, 문제에서 보기를 추출합니다|보기는 다음과 같습니다", 
                          " ", question)
        question = re.sub(r"\s+", " ", question)  # 여러 공백을 하나의 공백으로 대체
        return question.strip()  # 앞뒤 공백 제거

    def extract_options(self, question):
        parts = question.split("보기1")
        if len(parts) > 1:
            return "보기1 " + parts[1].strip()
        return ""

    def clean_response_column(self, question):
        # 보기 번호를 보기1, 보기2 등으로 변환
        question = question.replace("①", "보기1")
        question = question.replace("②", "보기2")
        question = question.replace("③", "보기3")
        question = question.replace("④", "보기4")
        question = question.replace("⑤", "보기5")
        question = question.replace("1.", "보기1")
        question = question.replace("2.", "보기2")
        question = question.replace("3.", "보기3")
        question = question.replace("4.", "보기4")
        question = question.replace("5.", "보기5")
        return question

    def process_json_files(self):
        pass

class ProcessorG1G2(BaseProcessor):
    def split_choices(self, row):
        if pd.isna(row):
            return {}
        pattern = re.compile(r'보기(\d) (.*?)(?=\s*보기\d|$)')
        matches = pattern.findall(row)
        choices = {f'choice{i}': '' for i in range(1, 6)}
        for match in matches:
            choice_num = int(match[0])
            choice_text = match[1].strip()
            choices[f'choice{choice_num}'] = choice_text
        return choices

    def process_json_files(self):
        json_files = [os.path.join(self.input_directory, filename) for filename in os.listdir(self.input_directory) if filename.endswith('.json')]
        
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        
        for file in json_files:
            data = pd.read_json(file)
            
            if 'question' in data.columns:
                data['question'] = data['question'].apply(self.clean_question_text)
                data['question'] = data['question'].apply(self.clean_response_column)
                data['choice'] = data['question'].apply(self.extract_options)
            
            if 'question_num' in data.columns:
                data.loc[data['question_num'] >= 22, 'choice'] = ""
            
            if 'choice' in data.columns:
                choices_df = data['choice'].apply(self.split_choices)
                choices_df = pd.json_normalize(choices_df)  # 딕셔너리를 데이터프레임으로 변환
                data = pd.concat([data, choices_df], axis=1)
                data = data.loc[:, ~data.columns.duplicated()]  # 중복된 컬럼 제거
                data = data.drop(columns=['choice','question'])  # 'choice' 컬럼 제거
            
            output_file = os.path.join(self.output_directory, os.path.basename(file))
            data.to_json(output_file, orient='records', force_ascii=False, indent=4)
            print(f"Processed and saved {file} to {output_file}")

class ProcessorG3(BaseProcessor):
    def split_choices(self, row):
        if pd.isna(row):
            return {}
        pattern = re.compile(r'보기(\d) (.*?)(?=\s*보기\d|$)')
        matches = pattern.findall(row)
        choices = {f'choice{i}': '' for i in range(1, 6)}
        for match in matches:
            choice_num = int(match[0])
            choice_text = match[1].strip()
            choices[f'choice{choice_num}'] = choice_text
        return choices
    
    def process_json_files(self):
        json_files = [os.path.join(self.input_directory, filename) for filename in os.listdir(self.input_directory) if filename.endswith('.json')]
        
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        
        for file in json_files:
            data = pd.read_json(file)
            
            if 'question' in data.columns:
                data['question'] = data['question'].apply(self.clean_question_text)
                data['question'] = data['question'].apply(self.clean_response_column)
                data['choice'] = data['question'].apply(self.extract_options)
            
            if len(data) < 30:
                new_question_nums = list(range(23, 23 + len(data)))
                data['question_num'] = new_question_nums
            
            if 'question_num' in data.columns:
                data.loc[data['question_num'].isin([16, 17, 18, 19, 20, 21, 22, 29, 30]), 'choice'] = ""

            if 'choice' in data.columns:
                choices_df = data['choice'].apply(self.split_choices)
                choices_df = pd.json_normalize(choices_df)  # 딕셔너리를 데이터프레임으로 변환
                data = pd.concat([data, choices_df], axis=1)
                data = data.loc[:, ~data.columns.duplicated()]  # 중복된 컬럼 제거
                data = data.drop(columns=['choice','question'])  # 'choice' 컬럼 제거
            
            
            output_file = os.path.join(self.output_directory, os.path.basename(file))
            data.to_json(output_file, orient='records', force_ascii=False, indent=4)
            print(f"Processed and saved {file} to {output_file}")