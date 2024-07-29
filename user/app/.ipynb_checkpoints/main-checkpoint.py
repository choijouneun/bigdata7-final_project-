from fastapi import Depends, FastAPI, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
import pandas as pd
from PIL import Image
from io import BytesIO
from img_vectorize import img_vector
import json
import os

app = FastAPI()
es = Elasticsearch("http://3.38.174.231:9200")

index_name = "question_korean"
model = SentenceTransformer('jhgan/ko-sbert-sts')

@app.post("/search/")
async def search(file: UploadFile = File(...)):
    file = await file.read()
    image = Image.open(BytesIO(file))
    image_embedding = img_vector(image)
    print(image_embedding)
    # embedding = model.encode(image_embedding, show_progress_bar=False)
    if not isinstance(image_embedding, list):
        image_embedding = image_embedding.tolist()
    script_query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": "cosineSimilarity(params.query_vector, 'image_vec') + 1.0",
                "params": {"query_vector": image_embedding[0]}
            }
        }
    }
    print("Script Query:", script_query)
    search_results = es.search(index=index_name, body={"query": script_query}, size=20)
    results = search_results["hits"]["hits"]
    return {"results": results}

# project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# app.mount("/static", StaticFiles(directory=os.path.join(project_dir, "static")), name="static")

# @app.get('/', response_class=FileResponse)
# async def read_index():
#     return FileResponse(os.path.join(project_dir, "static", "index.html"))

templates = Jinja2Templates(directory="templates")

@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "username": "Mina"})
