from config import ELASTIC_SETTING
from elasticsearch import Elasticsearch
import pandas as pd
import numpy as np
import sys
sys.path.append('/app/version')


def create_es_client():
    return Elasticsearch(
        [{'host': ELASTIC_SETTING['host'], 
          'port': ELASTIC_SETTING['port'], 
          'scheme': ELASTIC_SETTING['scheme']}]
    ).options(basic_auth=(ELASTIC_SETTING['username'], ELASTIC_SETTING['password']))

# Elasticsearch 클라이언트 생성
es = create_es_client()

# 벡터가 0벡터인지 확인하는 함수
def is_zero_vector(vector):
    return np.all(np.array(vector) == 0)

def is_valid_vector(vector):
    return np.isfinite(vector).all() and not is_zero_vector(vector)

def fetch_all_docs(index_name):
    # 모든 _id 값 가져오기
    query = {
        "query": {
            "match_all": {}
        },
        "size": 1000
    }

    # 스크롤을 사용하여 모든 문서의 _id와 벡터 값 가져오기(한번에 불러오면 서버 끊길 수 있음)
    all_docs = []
    scroll_id = None
    while True:
        if scroll_id:
            response = es.scroll(scroll_id=scroll_id, scroll='2m')
        else:
            response = es.search(index=index_name, body=query, scroll='2m')

        hits = response['hits']['hits']
        all_docs.extend([(hit['_id'], hit['_source']['image_vec'], hit['_source']['text_vec']) for hit in hits])

        if len(hits) == 0:
            break

        scroll_id = response['_scroll_id']

    # 스크롤 종료
    if scroll_id:
        es.clear_scroll(scroll_id=scroll_id)
    
    return all_docs

def find_similar_docs(index_name, all_docs, subject):
    similarity_data = []  # 유사도 데이터를 담을 리스트

    # 각 _id에 대해 유사한 20개의 문서를 찾음
    for origin_id, image_vec, text_vec in all_docs:
        if subject == 'ENG':  # 영어 과목은 이미지 벡터 먼저 유사도 돌리기
            primary_vec, secondary_vec = image_vec, text_vec
            primary_field, secondary_field = 'image_vec', 'text_vec'
        else:  # 국어, 수학 과목은 텍스트 벡터 먼저 유사도 돌리기
            primary_vec, secondary_vec = text_vec, image_vec
            primary_field, secondary_field = 'text_vec', 'image_vec'

        if not is_valid_vector(primary_vec):
            continue
        
        query = {
            "size": 20,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": f"cosineSimilarity(params.query_vector, '{primary_field}') + 1.0",
                        "params": {"query_vector": primary_vec}
                    }
                }
            }
        }
        response = es.search(index=index_name, body=query)
        
        for hit in response['hits']['hits']:
            similarity_id = hit['_id']
            similarity_primary_vec = hit['_source'][primary_field]
            similarity_secondary_vec = hit['_source'][secondary_field]

            if not is_valid_vector(secondary_vec) or not is_valid_vector(similarity_secondary_vec):
                continue

            sub_query = {
                "size": 1,
                "query": {
                    "script_score": {
                        "query": {
                            "term": {"_id": similarity_id}
                        },
                        "script": {
                            "source": f"cosineSimilarity(params.query_vector, '{secondary_field}') + 1.0",
                            "params": {"query_vector": secondary_vec}
                        }
                    }
                }
            }
            sub_response = es.search(index=index_name, body=sub_query)
            sub_similarity_value = sub_response['hits']['hits'][0]['_score']
            
            similarity_data.append({
                "origin_id": origin_id,
                "similarity_id": similarity_id,
                "similarity_value": sub_similarity_value - 1.0
            })
    
    return pd.DataFrame(similarity_data)