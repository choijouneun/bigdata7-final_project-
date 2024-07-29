import re
import pandas as pd

class CombinedProcessor:
    def __init__(self):
        pass

    def clean_question_text(self, question):
        # 불필요한 문자와 문자열 제거
        question = re.sub(r"\n|\\|plaintext|markdown|=|:|-|\*|선택지", " ", question)
        question = re.sub(r"다음은 추출된 보기 부분입니다|아래는 보기만 추출한 것입니다|"
                          r"보기만 추출해드리면 다음과 같습니다|좋습니다. 다음과 같이 보기를 추출할 수 있습니다|"
                          r"보기만 추출했어|다음은 예시에서 추출한 보기들입니다|"
                          r"당신이 예시로 준 '보기' 부분을 추출한 것처럼, 주어진 문제에서 보기 부분을 다음과 같이 추출할 수 있습니다|"
                          r"예시를 참고하여, 문제에서 보기를 추출합니다|보기는 다음과 같습니다", 
                          " ", question)
        question = re.sub(r"\s+", " ", question)  # 여러 공백을 하나의 공백으로 대체
        question = question.strip()  # 앞뒤 공백 제거
        return question  

    def extract_options_2(self, question):
        parts = question.split("보기1")
        if len(parts) > 1:
            return "보기1 " + parts[1].strip()
        return question
    
    def extract_options_1(self, question):
        parts = question.split("보기1")
        if len(parts) > 1:
            return parts[0].strip()
        return question

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
        question = question.replace("1)", "보기1")
        question = question.replace("2)", "보기2")
        question = question.replace("3)", "보기3")
        question = question.replace("4)", "보기4")
        question = question.replace("5)", "보기5")
        return question

    def extract_point(self, question):
        # 점수 추출
        match = re.search(r'\[(\d+)점\]', question)
        if match:
            return int(match.group(1))
        return 1

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

    def process_data(self, data):
        if 'question' in data.columns:
            data['question'] = data['question'].apply(self.clean_question_text)
            data['point'] = data['question'].apply(self.extract_point)
            data['question_1'] = data['question'].apply(self.clean_response_column)
            data['question'] = data['question_1'].apply(self.extract_options_1)
            data['choice'] = data['question_1'].apply(self.extract_options_2)
        
        if 'choice' in data.columns:
            choices_df = data['choice'].apply(self.split_choices)
            choices_df = pd.json_normalize(choices_df)  # 딕셔너리를 데이터프레임으로 변환
            data = pd.concat([data, choices_df], axis=1)
            data = data.drop(columns=['choice', 'question_1'])  # 'choice' 및 'question_1' 컬럼 제거

        return data