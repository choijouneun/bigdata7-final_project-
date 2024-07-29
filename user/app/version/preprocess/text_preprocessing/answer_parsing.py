import pandas as pd
import re

class AnswerProcessor:
    def __init__(self):
        pass

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

    def process_dataframe(self, df):
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

    def process_all_files(self, input_data):
        if isinstance(input_data, pd.DataFrame):
            return self.process_dataframe(input_data)
        else:
            raise ValueError("Input data should be a pandas DataFrame")
