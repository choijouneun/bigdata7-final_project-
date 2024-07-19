import os
import pandas as pd
import re

class QuestionProcessor:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory

        # JSON 저장 경로가 존재하지 않으면 생성
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def clean_question_text(self, question):
        # 불필요한 문자와 문자열 제거
        question = re.sub(r"\n|\\|plaintext|markdown|=|:|-|\*", " ", question)
        question = re.sub(r"다음은 추출된 보기 부분입니다|아래는 보기만 추출한 것입니다|보기만 추출해드리면 다음과 같습니다|"
                          r"좋습니다. 다음과 같이 보기를 추출할 수 있습니다|보기만 추출했어|다음은 예시에서 추출한 보기들입니다|"
                          r"당신이 예시로 준 '보기' 부분을 추출한 것처럼, 주어진 문제에서 보기 부분을 다음과 같이 추출할 수 있습니다|"
                          r"예시를 참고하여, 문제에서 보기를 추출합니다|보기는 다음과 같습니다", 
                          " ", question)
        question = re.sub(r"\s+", " ", question)  # 여러 공백을 하나의 공백으로 대체
        return question.strip()  # 앞뒤 공백 제거

    def extract_point(self, question):
        # 점수 추출
        match = re.search(r'\[(\d+)점\]', question)
        if match:
            return int(match.group(1))
        return None

    def clean_and_save_json_files(self):
        json_files = [os.path.join(self.input_directory, filename) for filename in os.listdir(self.input_directory) if filename.endswith('.json')]

        for file in json_files:
            data = pd.read_json(file)

            if 'question' in data.columns:
                data['question'] = data['question'].apply(self.clean_question_text)
                data['point'] = data['question'].apply(self.extract_point)

            # 전체 행이 30개 미만인 경우 'question_num'을 23, 24, 25, ...로 변경
            if len(data) < 30:
                new_question_nums = list(range(23, 23 + len(data)))
                data['question_num'] = new_question_nums

            output_file = os.path.join(self.output_directory, os.path.basename(file))
            data.to_json(output_file, orient='records', force_ascii=False, indent=4)
            print(f"Processed and saved {output_file}")
