import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModel
import torch

class TextEmbedder:
    def __init__(self, data):
        self.model_name = 'jhgan/ko-sbert-sts'
        self.columns_to_use = ['text','text_title','question', 'paragraph', 'choice1', 'choice2', 'choice3', 'choice4', 'choice5']
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name, output_hidden_states=True)
        self.data = self.load_and_prepare_data(data)
        

    def load_and_prepare_data(self, data):
        
        # 결합된 텍스트 생성
        data['combined_text'] = data.apply(lambda row: self.combine_columns(row, self.columns_to_use), axis=1)
        
        return data

    def combine_columns(self, row, columns):
        return ' '.join(row[col] for col in columns if pd.notnull(row[col]))

    def get_sentence_embedding(self, sentence):
        encoded_input = self.tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
        input_ids = encoded_input['input_ids'].long()
        with torch.no_grad():
            outputs = self.model(input_ids=input_ids, attention_mask=encoded_input['attention_mask'])
            embeddings = outputs.last_hidden_state.mean(1)
        return embeddings.detach().numpy()

    def compute_embeddings(self):
        self.data['text_embeddings'] = self.data['combined_text'].apply(lambda x: self.get_sentence_embedding(x).flatten())
        return np.vstack(self.data['text_embeddings'].values)