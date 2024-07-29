import sys
import os
import pandas as pd
from preprocess.kor_text_preprcessing import OpenAIImageQuestioner
from preprocess.kor_choice_preprocessing import Processor
from preprocess.kor_question_preprocessing import QuestionProcessor
from preprocess.kor_merge_json import JSONMerger
from preprocess.imagecrop import ImageCropper
from preprocess.kor_text_preprocessing import TextProcessor

class ImageQuestionProcessingPipeline:
    def __init__(self, image_file):
        self.image_file = image_file
        self.api_key = "sk-proj-3JUo4EwKOKPcoterMJVST3BlbkFJlrgUmwrvlEKN9Nlv3uik"  # API 키를 내부에 설정
        self.base_directory = os.path.dirname(os.path.abspath(__file__))  # 현재 작업 디렉토리를 기본 디렉토리로 설정
        self.output_directory_1 = os.path.join(self.base_directory, "crop_pra")
        self.output_directory_2 = os.path.join(self.base_directory, "crop_pra_2")

        # Create instances of the classes
        self.cropper = ImageCropper(image_file, self.output_directory_1, self.output_directory_2)
        self.questioner_1 = OpenAIImageQuestioner(self.api_key,self.output_directory_1)
        self.questioner_2 = OpenAIImageQuestioner(self.api_key,self.output_directory_2)
        self.questioner_3 = OpenAIImageQuestioner(self.api_key,self.output_directory_2)

        # Ensure output directories exist
        self.setup_directories()

    def setup_directories(self):
        if not os.path.exists(self.output_directory_1):
            os.makedirs(self.output_directory_1)
        if not os.path.exists(self.output_directory_2):
            os.makedirs(self.output_directory_2)

    def process_choices(self, data):
        processor = Processor()
        return processor.process_data(data)

    def process_questions(self, data):
        question_processor = QuestionProcessor()
        return question_processor.clean_and_process_data(data)

    def process_text(self, data):
        text_processor = TextProcessor()
        return text_processor.clean_and_process_data(data)

    def merge_data(self, df1, df2, df3):
        json_merger = JSONMerger()
        return json_merger.merge_dataframes(df1, df2, df3)

    def run(self):
        # 이미지 크롭 처리
        self.cropper.process_image()

        # 질문 설정
        questions_1 = [
            "모든 텍스트 추출해줘"
        ]
        questions_2 = [
            "문제만 추출해줘"
        ]
        questions_3 = [
            "보기1, 보기2, 보기3, 보기4, 보기5 를 추출해줘"
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
        # 보기(choice)
        results_3 = []
        for question in questions_3:
            results_3.extend(self.questioner_3.process_images(question))
        
        # 결과 출력 또는 저장
        print(f"Results 1: {results_1}")
        print(f"Results 2: {results_2}")
        print(f"Results 3: {results_3}") 

        # 선택지 처리
        df_choices = pd.DataFrame(results_3)
        df_questions = pd.DataFrame(results_2)
        df_texts = pd.DataFrame(results_1)

        # 선택지 처리
        processed_choices = self.process_choices(df_choices)

        # 질문 처리
        processed_questions = self.process_questions(df_questions)

        # 지문 처리
        processed_texts = self.process_text(df_texts)

        # JSON 데이터 병합
        merged_data = self.merge_data(processed_texts, processed_questions, processed_choices)

        # 병합된 데이터 출력
        print(f"Merged Data: {merged_data}")
        return merged_data
