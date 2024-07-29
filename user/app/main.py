from fastapi import FastAPI, HTTPException, UploadFile, File, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from PIL import Image
from io import BytesIO
from img_vectorize import img_vector
import sys
import easyocr
from kor_pipeline import ImageQuestionProcessingPipeline as kor_pi
from eng_pipeline import Engpipeline as eng_pi
from math_pipeline import Mathpipeline as math_pi
from embedding.text_embedd import TextEmbedder 
from embedding.text_embedd_eng import TextEmbedder as eng_embed
import s3fs
import pandas as pd
import shutil
import os
import uuid
from config import DB_SETTING
import pymysql
from version.main import main

app = FastAPI()
es = Elasticsearch("http://3.38.174.231:9200")
app.mount("/static", StaticFiles(directory="static"), name="static")
index_names = ["questions_korean", "questions_math", "questions_english"]
model = SentenceTransformer('jhgan/ko-sbert-sts')
bucket_name = 'big7-similarity-bucket'
reader = easyocr.Reader(['ko', 'en'])
fs = s3fs.S3FileSystem()
templates = Jinja2Templates(directory="templates")
results = {}

# 사용자 문제 db저장(mariadb)
def save_to_mariadb(df, table_name):
    connection = pymysql.connect(
        host=DB_SETTING['host'],
        user=DB_SETTING['user'],
        password=DB_SETTING['password'],
        database=DB_SETTING['database'],
        port=DB_SETTING['port']
    )
    try:
        with connection.cursor() as cursor:
            create_table_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                question_id VARCHAR(100),
                directory VARCHAR(100),
                similarity_id VARCHAR(20),
                similarity_value FLOAT
            )
            """
            cursor.execute(create_table_query)
            connection.commit()
            insert_query = f"""
            INSERT INTO {table_name} (question_id, directory, similarity_id, similarity_value)
            VALUES (%s, %s, %s, %s)
            """
            for _, row in df.iterrows():
                cursor.execute(insert_query, (row['origin_id'], row['directory'], row['similarity_id'], row['similarity_value']))
            connection.commit()
    finally:
        connection.close()
    print(f"{table_name} 테이블에 데이터 적재 성공!")

# 메인페이지(이미지, pdf업로드)
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 유사도 결과 띄우기 위해 서버에 임시 저장한 이미지 파일 삭제
@app.get("/delete_temp_images")
def delete_temp_images():
    temp_img_dir = "static/temp_img"
    try:
        if (os.path.exists(temp_img_dir)):
            shutil.rmtree(temp_img_dir)
            os.makedirs(temp_img_dir)
        return RedirectResponse(url="/")
    except Exception as e:
        return {"status": "error", "message": str(e)}

# 사용자 문항 이미지 업로드
@app.post("/upload_image/")
async def upload_image(background_tasks: BackgroundTasks, request: Request, file: UploadFile = File(...), subject: str = Form(...)):
    file_location = f"./{file.filename}"
    file_id = str(uuid.uuid4())
    original_location = file_location
    file_content = await file.read()

    with open(file_location, "wb") as f:
        f.write(file_content)

    image = Image.open(BytesIO(file_content))
    image_embedding = img_vector(image)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(current_dir)
    sys.path.append(os.path.join(current_dir, 'prompt'))

    # 단일 이미지 파일 경로 설정
    similarity_data = []
    image_file = file_location

    background_tasks.add_task(process_image, file_location, image_file, subject, file_id, image_embedding, similarity_data, image, original_location)

    results[file_id] = {
        "data": similarity_data,
        "processed": False,  # 아직 처리가 완료되지 않았음을 나타냄
        "original_image": file_id
    }
    
    return templates.TemplateResponse("similarity_result.html", {"request": request, "file_id": file_id})
    # return templates.TemplateResponse("similarity_result.html", {"request": request, "results": sorted(similarity_data, key=lambda x: x['similarity_value'], reverse=True)})

def process_image(file_location, image_file, subject, file_id, image_embedding, similarity_data, image, original_location):
    # 과목별 텍스트 파싱 및 임베딩 순서 설정
    if subject == 'questions_korean':
        pipeline = kor_pi(file_location).run()
        sub_dir = "KOR"
        text_embedding = TextEmbedder(pipeline).compute_embeddings()
        primary_vec, secondary_vec = text_embedding, image_embedding
        primary_field, secondary_field = 'text_vec', 'image_vec'
    elif subject == 'questions_math':
        pipeline = math_pi(file_location).run()
        sub_dir = "MATH"
        text_embedding = TextEmbedder(pipeline).compute_embeddings()
        primary_vec, secondary_vec = text_embedding, image_embedding
        primary_field, secondary_field = 'text_vec', 'image_vec'
    else:
        pipeline = eng_pi(file_location).run()
        sub_dir = "ENG"
        text_embedding = eng_embed(pipeline).compute_embeddings()
        # primary_vec, secondary_vec = text_embedding, image_embedding
        # primary_field, secondary_field = 'text_vec', 'image_vec'
        primary_vec, secondary_vec = image_embedding, text_embedding
        primary_field, secondary_field = 'image_vec', 'text_vec'

    if not isinstance(image_embedding, list):
        image_embedding = image_embedding.tolist()
    origin_id = sub_dir + '_' + file_id + ".png"
    query = {
        "script_score": {
            "query": {"match_all": {}},
            "script": {
                "source": f"cosineSimilarity(params.query_vector, '{primary_field}') + 1.0",
                "params": {"query_vector": primary_vec[0]}
            }
        }
    }
    response = es.search(index=subject, body={"query": query}, size=20)
    for hit in response['hits']['hits']:
        similarity_id = hit['_id']
        sub_query = {
            "size": 1,
            "query": {
                "script_score": {
                    "query": {
                        "term": {"_id": similarity_id}
                    },
                    "script": {
                        "source": f"cosineSimilarity(params.query_vector, '{secondary_field}') + 1.0",
                        "params": {"query_vector": secondary_vec[0]}
                    }
                }
            }
        }
        sub_response = es.search(index=subject, body=sub_query)
        sub_similarity_value = sub_response['hits']['hits'][0]['_score']
        
        similarity_data.append({
            "subject": subject,
            "origin_id": origin_id,
            "similarity_id": similarity_id,
            "similarity_value": sub_similarity_value - 1.0,
            "file_name": None
        })
    sorted_similarity_data = sorted(similarity_data, key=lambda x: x['similarity_value'], reverse=True)

    for data in sorted_similarity_data:
        grade = data['similarity_id'][0:2]
        year = data['similarity_id'][2:6]
        month = data['similarity_id'][6:8]
        category = data['similarity_id'][8:10]
        number = data['similarity_id'][11:]
        if len(number) == 1:
            number = '0' + number
        if subject == "questions_korean":
            subject_name = "KOR"
            file_name = f"KOR_{grade}_{year}_{month}_{number}"
            if category == "02":# 화작
                file_name = f"KOR_{grade}_{year}_{month}_speech_writing_{number}"
            elif category == "03":# 언매
                file_name = f"KOR_{grade}_{year}_{month}_language_media_{number}"
        elif subject == "questions_math":
            subject_name = "MATH"
            file_name = f"MATH_{grade}_{year}_{month}_{number}"
            if category == "02":# 가
                file_name = f"MATH_{grade}_{year}_{month}_A_{number}"
            elif category == "03":# 나
                file_name = f"MATH_{grade}_{year}_{month}_B_{number}"
            elif category == "04":# 확통
                file_name = f"MATH_{grade}_{year}_{month}_statistics_{number}"
            elif category == "05":# 미적
                file_name = f"MATH_{grade}_{year}_{month}_calculus_{number}"
            elif category == "06":# 기하
                file_name = f"MATH_{grade}_{year}_{month}_geometry_{number}"
        else:
            subject_name = "ENG"
            file_name = f"ENG_{grade}_{year}_{month}_{number}"
        temp_dir = os.path.join(os.path.dirname(__file__), "static/temp_img")
        os.makedirs(temp_dir, exist_ok=True)

        file_location = os.path.join(temp_dir, file_name)
        local_file_path = f'static/temp_img/{file_name}.png'

        try:
            file_path = f'workbook/{subject_name}/grade{grade[1]}/{year}/{month}/image/{file_name}.png'
            with fs.open(f's3://{bucket_name}/{file_path}', 'rb') as f:
                img = Image.open(f)
                img = img.convert("RGB")  # Ensure image is in RGB format
                img.save(local_file_path)
            data["file_name"] = file_name

        except Exception as e:
            print(f'Error loading image: {file_path}, {e}')
    original_dir = 'static/temp_img/original.png'
    s3_dir = f'external-user-questions/{sub_dir}/{origin_id}'
    image.save(original_dir)
    
    with open(original_dir, 'rb') as local_file:
        with fs.open(f's3://{bucket_name}/external-user-questions/{sub_dir}/{origin_id}', 'wb') as s3_file:
            s3_file.write(local_file.read())

    if subject == 'questions_korean':
        try:
            shutil.rmtree("crop_pra")
            shutil.rmtree("crop_pra_2")
        except Exception as e:
            print(f"폴더 삭제 중 오류가 발생했습니다: {e}")
    try:
        os.remove(original_location)
    except Exception as e:
        print(f"파일 삭제 중 오류가 발생했습니다: {e}")

    df = pd.DataFrame(sorted_similarity_data)[['similarity_id', 'similarity_value']]
    df['origin_id'] = origin_id
    df['directory'] = s3_dir

    if subject == 'questions_korean':
        table_name = "user_similarity_korean"
    if subject == 'questions_math':
        table_name = "user_similarity_math"
    if subject == 'questions_english':
        table_name = "user_similarity_english"

    save_to_mariadb(df, table_name)

    results[file_id]["processed"] = True

@app.get("/get_results/{file_id}")
async def get_results(file_id: str):
    if file_id in results:
        return JSONResponse(content=results[file_id])
    else:
        raise HTTPException(status_code=404, detail="File ID not found")

@app.post("/upload_pdf/")
async def upload_pdf(pdf_file: UploadFile = File(...), img_file: UploadFile = File(...), subject: str = Form(...), grade: str = Form(...), year: str = Form(...), month: str = Form(...), section: str = Form(...)):
    if pdf_file.content_type != 'application/pdf':
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    if img_file.content_type not in ['image/jpeg', 'image/png', 'image/jpg']:
        raise HTTPException(status_code=400, detail="Only image files (JPEG, JPG, PNG) are allowed.")
    
    if section != '공통':
        if section == '언어와 매체':
            section_name = 'language_media'
        elif section == '화법과 작문':
            section_name = 'speech_writing'
        elif section == '가형':
            section_name = 'A'
        elif section == '나형':
            section_name = 'B'
        elif section == '확률과 통계':
            section_name = 'statistics'
        elif section == '미적분':
            section_name = 'calculus'
        elif section == '기하':
            section_name = 'geometry'
        custom_filename = f"{subject}_{grade}_{year}_{month}_{section_name}"
    else:
        custom_filename = f"{subject}_{grade}_{year}_{month}"

    pdf_dir = os.path.join(os.path.dirname(__file__), "temp_pdf")
    os.makedirs(pdf_dir, exist_ok=True)

    file_location = os.path.join(pdf_dir, custom_filename)
    file_location = file_location + ".pdf"

    with open(file_location, "wb") as f:
        f.write(await pdf_file.read())

    img_dir = os.path.join(pdf_dir, custom_filename+"_answer")
    os.makedirs(img_dir, exist_ok=True)

    image_save_path = os.path.join(img_dir, custom_filename)

    contents = await img_file.read()
    image = Image.open(BytesIO(contents))
    
    image.save(image_save_path+'.png', format="PNG")

    # /home/ubuntu/workspace/version/main.py 실행
    # subprocess.run(["python3", "/home/ubuntu/workspace/version/main.py", subject])
    main(subject)
    
    return {"filename": custom_filename, "content_type": pdf_file.content_type, "saved_to": file_location}
