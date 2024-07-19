import os
import pandas as pd
import json
import glob

class JSONMerger:
    def __init__(self, input_dir_1, input_dir_2, input_dir_3, input_dir_4, output_dir):
        self.input_dir_1 = input_dir_1
        self.input_dir_2 = input_dir_2
        self.input_dir_3 = input_dir_3
        self.input_dir_4 = input_dir_4
        self.output_dir = output_dir

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def load_json_to_dataframe(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.strip() == "":  # 파일이 비어있는지 확인
                print(f"{file_path} is empty. Returning empty DataFrame.")
                return pd.DataFrame()  # 빈 DataFrame 반환
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                print(f"Error decoding JSON from file: {file_path}")
                return pd.DataFrame()  # 오류가 발생해도 빈 DataFrame 반환
        return pd.json_normalize(data)

    def save_dataframe_to_json(self, df, output_file):
        if df is not None and not df.empty:
            json_data = df.to_dict(orient='records')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=4)
            print(f"JSON 파일로 저장 완료: {output_file}")
        else:
            print(f"No data to save for {output_file}")

    def process_files(self):
        question_file = glob.glob(os.path.join(self.input_dir_1, "*.json"))[0]
        answer_file_1 = glob.glob(os.path.join(self.input_dir_2, "*.json"))[0]
        answer_file_2 = glob.glob(os.path.join(self.input_dir_3, "*.json"))[0]
        answer_file_3 = glob.glob(os.path.join(self.input_dir_4, "*.json"))[0]
        
        df1 = self.load_json_to_dataframe(question_file)
        df2 = self.load_json_to_dataframe(answer_file_1)
        df3 = self.load_json_to_dataframe(answer_file_2)
        df4 = self.load_json_to_dataframe(answer_file_3)

        # Merge df2
        if df2 is not None and not df2.empty:
            df1 = pd.merge(df1, df2, on='question_num', how='left')
        
        # Merge df3
        if df3 is not None and not df3.empty:
            df1 = pd.merge(df1, df3, on='question_num', how='left')
        
        # Merge df4
        if df4 is not None and not df4.empty:
            df1 = pd.merge(df1, df4, on='question_num', how='left')
        
        output_file = os.path.join(self.output_dir, os.path.basename(question_file))
        self.save_dataframe_to_json(df1, output_file)