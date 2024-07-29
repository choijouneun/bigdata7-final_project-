import pandas as pd
from preprocess.math_text_preprocessing import OpenAIImageQuestioner
from preprocess.math_choice_preprocessing import Processor

class Mathpipeline:
    def __init__(self, image_path):
        self.api_key = "sk-proj-3JUo4EwKOKPcoterMJVST3BlbkFJlrgUmwrvlEKN9Nlv3uik"
        self.question = "내가 준 이미지내 텍스트만 출력해줘"
        self.image_path = image_path
        self.questioner_1 = OpenAIImageQuestioner(self.api_key)

    def run(self):
        # Process the image with the question
        result = self.questioner_1.process_image(self.image_path, self.question)

        # 선택지 처리
        if result:
            processor = Processor()
            processed_choices = processor.process_json_data([result])
            return processed_choices
        else:
            print("No valid responses to process.")
            return None