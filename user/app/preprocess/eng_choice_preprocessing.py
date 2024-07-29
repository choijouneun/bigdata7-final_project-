import pandas as pd

class Processor:
    def __init__(self):
        pass

    def add_and_reorder_columns(self, data):
        additional_columns = {
            "text_title": "",
            "text_yn": "",
            "text_exp": "",
            "question_exp": "",
            "grade": "",
            "yyyy": "",
            "mm": "",
            "subject_cat": "",
            "host": "",
            "multiple_answer": "",
            "short_answer": "",
            "question_cat": "",
            'choice1':"",
            'choice2':"",
            'choice3':"",
            'choice4':"",
            'choice5':"",
            'text':"",
            "paragraph":""
        }
        for col, default_value in additional_columns.items():
            data[col] = default_value
        columns_order = ['grade', 'yyyy', 'mm', 'host', 'subject_cat', 'question_cat', 'question_num', 'points', 
                         'text_title', 'text', 'text_yn', 'question', 'paragraph', 'choice1', 'choice2', 'choice3', 
                         'choice4', 'choice5', 'short_answer', 'multiple_answer', 'text_exp', 'question_exp']

        # 존재하지 않는 컬럼은 무시하고 재정렬
        data = data.reindex(columns=[col for col in columns_order if col in data.columns])
        return data