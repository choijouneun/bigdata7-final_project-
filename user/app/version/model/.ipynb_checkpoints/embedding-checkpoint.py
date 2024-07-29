import sys
sys.path.append('..')

import numpy as np
import torch
import clip
from transformers import AutoTokenizer, AutoModel


class ImageEmbedding:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model, self.preprocess = clip.load("ViT-B/32", device=self.device)

    def get_image_embedding(self, img):
        img = self.preprocess(img).unsqueeze(0).to(self.device)
        with torch.no_grad():
            features = self.model.encode_image(img)
        return features.cpu().numpy().flatten()

class TextEmbedding:
    def __init__(self):
        text_model_name = 'jhgan/ko-sbert-sts'
        self.tokenizer = AutoTokenizer.from_pretrained(text_model_name)
        self.model = AutoModel.from_pretrained(text_model_name, output_hidden_states=True)

    def embed_texts(self, texts, batch_size=32):
        embeddings = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            inputs = self.tokenizer(batch_texts, return_tensors='pt', padding=True, truncation=True)
            with torch.no_grad():
                outputs = self.model(**inputs)
            batch_embeddings = outputs.last_hidden_state.mean(dim=1)
            embeddings.extend(batch_embeddings)
        return torch.stack(embeddings)