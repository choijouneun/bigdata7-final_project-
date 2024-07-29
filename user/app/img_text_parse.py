from dotenv import load_dotenv
import os
import base64
import requests
import json
import torch
from PIL import Image
from transformers import AutoTokenizer, AutoModel
import easyocr
import re

load_dotenv()
api_key = os.getenv('API_KEY')

# OCR 리더와 텍스트 임베딩 모델 초기화
reader = easyocr.Reader(['ko', 'en'])
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/bert-base-nli-mean-tokens")
model = AutoModel.from_pretrained("sentence-transformers/bert-base-nli-mean-tokens")

device = "cuda" if torch.cuda.is_available() else "cpu"
model = model.to(device)

def extract_text_from_image(image: Image.Image) -> str:
    # easyOCR를 사용하여 이미지에서 텍스트 추출
    results = reader.readtext(image)
    extracted_text = ' '.join([result[1] for result in results])
    return extracted_text

def text_to_embedding(text: str):
    # 텍스트 토큰화
    tokens = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
    tokens = {key: value.to(device) for key, value in tokens.items()}
    
    # 모델에서 임베딩 생성
    with torch.no_grad():
        embeddings = model(**tokens)
    
    # 임베딩의 평균을 사용하여 단일 벡터 생성
    embedding = embeddings.last_hidden_state.mean(dim=1).cpu().numpy()
    return embedding

def img_text_parse(image: Image.Image):
    try:
        # 이미지에서 텍스트 추출
        text = extract_text_from_image(image)
        
        # 추출한 텍스트 정리
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 텍스트 임베딩 생성
        text_embedding = text_to_embedding(text)
        
        return text, text_embedding
    except Exception as e:
        print('이미지 텍스트 파싱 중 예외가 발생했습니다:', e)
        return None, None