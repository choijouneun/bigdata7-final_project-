import pandas as pd
import re
import os

class AnswerProcessor:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory
        os.makedirs(self.output_directory, exist_ok=True)

    def load_data(self, input_file):
        # JSON 파일을 데이터프레임으로 불러오기
        return pd.read_json(input_file)

    def extract_answers(self, text):
        # 특수 기호를 숫자로 변환
        conversion_dict = {
            '①': '1',
            '②': '2',
            '③': '3',
            '④': '4',
            '⑤': '5'
        }
        for k, v in conversion_dict.items():
            text = text.replace(k, v)
        
        # 정규표현식 패턴
        pattern = re.compile(r'(\d+)\.\s*([\d]+)')
        matches = pattern.findall(text)
        answers = {int(num): answer for num, answer in matches}
        return answers

    def process_file(self, input_file):
        df = self.load_data(input_file)
        # 정규표현식을 사용하여 'question' 컬럼에서 문제 번호와 답 추출
        df['extracted_answers'] = df['question'].apply(self.extract_answers)

        # 추출된 답안을 행으로 분할
        rows = []
        for index, row in df.iterrows():
            for question_num, answer in row['extracted_answers'].items():
                row_data = {
                    'question_num': question_num,
                    'multiple_answer': int(answer) if question_num in range(1, 16) or question_num in range(23, 29) else "",
                    'short_answer': int(answer) if question_num in range(16, 22) or question_num in [29, 30] else ""
                }
                rows.append(row_data)

        # 새로운 데이터프레임 생성
        expanded_df = pd.DataFrame(rows)
        return expanded_df

    def process_all_files(self):
        json_files = [f for f in os.listdir(self.input_directory) if f.endswith('.json')]

        for json_file in json_files:
            input_file_path = os.path.join(self.input_directory, json_file)
            output_file_path = os.path.join(self.output_directory, json_file)

            expanded_df = self.process_file(input_file_path)

            # 결과를 새로운 JSON 파일로 저장
            expanded_df.to_json(output_file_path, orient='records', force_ascii=False, indent=4)
            print(f"Processed and saved {output_file_path}")

