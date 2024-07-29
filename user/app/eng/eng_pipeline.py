import pandas as pd
from preprocess.eng_text_preprocessing import OpenAIImageQuestioner
from preprocess.eng_choice_preprocessing import Processor

class Engpipeline:
    def __init__(self, image_path):
        self.api_key = api_key 
        self.question = "내가 준 이미지내 텍스트만 출력해줘"
        self.image_path = image_path
        self.questioner_1 = OpenAIImageQuestioner(self.api_key)

    def run(self):
        # Process the image with the question
        result = self.questioner_1.process_image(self.image_path, self.question)

        # 선택지 처리
        if result:
            processor = Processor()
            # 리스트를 DataFrame으로 변환
            result_df = pd.DataFrame([result])
            processed_choices = processor.process_data(result_df)
            return processed_choices
        else:
            print("No valid responses to process.")
            return None
