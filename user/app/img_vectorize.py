from PIL import Image
import torch
import clip

# es = Elasticsearch("http://3.38.174.231:9200")

# index_name = "questions_math"
# query = {
#     "query":{
#         "match_all": {}
#     }
# }

# response = es.search(index=index_name, body=query)
# count = response['hits']['total']['value']
# response = es.search(index=index_name, body=query, size=count)

# hits = response['hits']['hits']

# data = [hit['_source'] for hit in hits]
# df = pd.DataFrame(data)
# embedding = model.encode(file, show_progress_bar=False)


device = "cuda" if torch.cuda.is_available() else "cpu"
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