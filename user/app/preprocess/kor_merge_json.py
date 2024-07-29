import pandas as pd

class JSONMerger:
    def __init__(self):
        pass

    def merge_dataframes(self, df1, df2):
        print("Dataframe shapes before merge:")
        print(f"df1: {df1.shape}, df2: {df2.shape}")

        # Merge df2
        if df2 is not None and not df2.empty:
            df1 = pd.merge(df1, df2, on='question_num', how='left')
            print(f"Shape after merging df1 with df2: {df1.shape}")
        else:
            print("df2 is empty or None, skipping merge with df2.")

        # 컬럼 순서 재정렬
        columns_order = ['grade', 'yyyy', 'mm', 'host', 'subject_cat', 'question_cat', 'question_num', 'points', 
                         'text_title', 'text', 'text_yn', 'question', 'paragraph', 'choice1', 'choice2', 'choice3', 
                         'choice4', 'choice5', 'short_answer', 'multiple_answer', 'text_exp', 'question_exp']
        
        # 존재하지 않는 컬럼은 빈값으로 채우고 재정렬
        for col in columns_order:
            if col not in df1.columns:
                df1[col] = pd.NA
                
        df1 = df1[columns_order]

        return df1

