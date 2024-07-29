import sys
import os
import pandas as pd
from preprocess.kor_text_preprcessing import OpenAIImageQuestioner
from preprocess.kor_merge_json import JSONMerger
from preprocess.imagecrop import ImageCropper
from preprocess.kor_text_preprocessing import TextProcessor
from preprocess.kor_combined import CombinedProcessor

class ImageQuestionProcessingPipeline:
    def __init__(self, image_file):
        self.image_file = image_file
        self.api_key = api_key   # API 키를 내부에 설정
        self.base_directory = os.path.dirname(os.path.abspath(__file__))  # 현재 작업 디렉토리를 기본 디렉토리로 설정
        self.output_directory_1 = os.path.join(self.base_directory, "crop_pra")
        self.output_directory_2 = os.path.join(self.base_directory, "crop_pra_2")

        # Create instances of the classes
        self.cropper = ImageCropper(image_file, self.output_directory_1, self.output_directory_2)
        self.questioner_1 = OpenAIImageQuestioner(self.api_key,self.output_directory_1)
        self.questioner_2 = OpenAIImageQuestioner(self.api_key,self.output_directory_2)

        # Ensure output directories exist
        self.setup_directories()

    def setup_directories(self):
        if not os.path.exists(self.output_directory_1):
            os.makedirs(self.output_directory_1)
        if not os.path.exists(self.output_directory_2):
            os.makedirs(self.output_directory_2)

    
    def process_text(self, data):
        text_processor = TextProcessor()
        return text_processor.clean_and_process_data(data)

    def merge_data(self, df1, df2):
        json_merger = JSONMerger()
        return json_merger.merge_dataframes(df1, df2)

    def run(self):
        # 이미지 크롭 처리
        self.cropper.process_image()

        # 질문 설정
        questions_1 = [
"""Role : 국어선생님

Task : 이미지내 텍스트를 모두 추출해줘

Format : ...다했습니다. 추출했습니다. 같이 쓸데없는말 넣지말고 이미지내 텍스트만 추출한 것만 답변해줘"""
        ]
        questions_2 = [
            """Role : 국어선생님

Task : 이미지내 텍스트를 모두 추출해줘

Format : ...다했습니다. 추출했습니다. 같이 쓸데없는말 넣지말고 이미지내 텍스트만 추출한 것만 답변해줘"""
        ]

        # Process images with questions
        # 지문(text)
        results_1 = []
        for question in questions_1:
            results_1.extend(self.questioner_1.process_images(question))
        # 문제(question)
        results_2 = []
        for question in questions_2:
            results_2.extend(self.questioner_2.process_images(question))


        
        # 결과 출력 또는 저장
        print(f"Results 1: {results_1}")
        print(f"Results 2: {results_2}")


        # 선택지 처리
        df_questions = pd.DataFrame(results_2)
        df_texts = pd.DataFrame(results_1)
        df_questions.to_json(r'C:\Users\BIG3-04\Downloads\df.json',orient='records',lines=True)
        # 선택지 처리
        processed_texts = self.process_text(df_texts)

        # 질문 처리
        
        # JSON 데이터 병합
        merged_data = self.merge_data(df_questions, processed_texts)
        merged_data.to_json(r'C:\Users\BIG3-04\Downloads\df.json',orient='records',lines=True)
        # 병합된 데이터 출력
        print(f"Merged Data: {merged_data}")
        return merged_data
