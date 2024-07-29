from PIL import Image
import torch
import clip
from sentence_transformers import SentenceTransformer

device = "cuda" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer('jhgan/ko-sbert-sts')
vec_model, preprocess = clip.load("ViT-B/32", device=device)

def img_vector(file):
    try:
        img = preprocess(file).unsqueeze(0).to(device)
        with torch.no_grad():
            image_features = vec_model.encode_image(img)
        return image_features.cpu().numpy()
    except Exception as e:
        print('예외가 발생했습니다.', e)
        return None