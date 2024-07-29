import pandas as pd
import re

class TextProcessor:
    def __init__(self):
        pass

    def clean_question_text(self, question):
        # 불필요한 문자와 문자열 제거
        question = re.sub(r"\n|\\|plaintext|markdown|=|:|-|\*", " ", question)
        question = re.sub(r"다음은 추출된 보기 부분입니다|아래는 보기만 추출한 것입니다|보기만 추출해드리면 다음과 같습니다|"
                          r"좋습니다. 다음과 같이 보기를 추출할 수 있습니다|보기만 추출했어|다음은 예시에서 추출한 보기들입니다|"
                          r"당신이 예시로 준 '보기' 부분을 추출한 것처럼, 주어진 문제에서 보기 부분을 다음과 같이 추출할 수 있습니다|"
                          r"예시를 참고하여, 문제에서 보기를 추출합니다|보기는 다음과 같습니다", 
                          " ", question)
        question = re.sub(r"\s+", " ", question)  # 여러 공백을 하나의 공백으로 대체
        question = question.strip()  # 앞뒤 공백 제거
        return question 

    def clean_and_process_data(self, data):
        if 'question' in data.columns:
            data['text'] = data['question'].apply(self.clean_question_text)
            data = data.drop(columns=['question'])
        return data