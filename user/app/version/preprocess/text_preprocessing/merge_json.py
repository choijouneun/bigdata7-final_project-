import os
import pandas as pd
import json

class JSONMerger:
    def __init__(self, output_dir):
        self.output_dir = output_dir

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def save_dataframe_to_json(self, df, output_file):
        if df is not None and not df.empty:
            json_data = df.to_dict(orient='records')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            print(f"JSON 파일로 저장 완료: {output_file}")
        else:
            print(f"No data to save for {output_file}")

    def merge_dataframes(self, df1, df2, df3, df4):
        print("Dataframe shapes before merge:")
        print(f"df1: {df1.shape}, df2: {df2.shape}, df3: {df3.shape}, df4: {df4.shape}")

        # Merge df2
        if df2 is not None and not df2.empty:
            df1 = pd.merge(df1, df2, on='question_num', how='left')
            print(f"Shape after merging df1 with df2: {df1.shape}")

        # Merge df3
        if df3 is not None and not df3.empty:
            df1 = pd.merge(df1, df3, on='question_num', how='left')
            print(f"Shape after merging df1 with df3: {df1.shape}")

        # Merge df4
        if df4 is not None and not df4.empty:
            df1 = pd.merge(df1, df4, on='question_num', how='left')
            print(f"Shape after merging df1 with df4: {df1.shape}")
        
        columns_order = ['grade', 'yyyy', 'mm', 'host', 'subject_cat', 'question_cat', 'question_num', 'points', 
                         'text_title', 'text', 'text_yn', 'question', 'paragraph', 'choice1', 'choice2', 'choice3', 
                         'choice4', 'choice5', 'short_answer', 'multiple_answer', 'text_exp', 'question_exp']
        
        # 존재하지 않는 컬럼은 무시하고 재정렬
        df1 = df1.reindex(columns=[col for col in columns_order if col in df1.columns])

        output_file = os.path.join(self.output_dir, 'MATH_G3_2024_06_calculus.json')
        self.save_dataframe_to_json(df1, output_file)

    def process_dataframes(self, df1, df2, df3, df4):
        self.merge_dataframes(df1, df2, df3, df4)