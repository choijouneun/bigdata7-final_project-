import time
from elasticsearch import Elasticsearch, helpers
import sys
sys.path.append('/app/version')
from config import ELASTIC_SETTING

class ElasticManager:
    """
    Elasticsearch 관리하는 클래스
    - es 클라이언트 생성
    - create_index : 인덱스 생성
    - delete_index : 인덱스 삭제
    - add_documents : 데이터 한번에 업로드
    """
    def __init__(self):
        self.es = Elasticsearch(
            [{'host': ELASTIC_SETTING['host'], 
              'port': ELASTIC_SETTING['port'], 
              'scheme': ELASTIC_SETTING['scheme']}]
        ).options(basic_auth=(ELASTIC_SETTING['username'], ELASTIC_SETTING['password']))

    def index_exists(self, index_name):
        return self.es.indices.exists(index=index_name)

    def create_index(self, index_name):
        mappings = {
            "mappings": {
                "properties": {
                    "text_vec": {"type": "dense_vector", "dims": 768},
                    "image_vec": {"type": "dense_vector", "dims": 512}
                }
            }
        }
        if not self.es.indices.exists(index=index_name):
            self.es.indices.create(index=index_name, body=mappings)
            print('인덱스 생성 성공!')
        else:
            print(f"{index_name} 인덱스 이미 존재")

    def delete_index(self, index_name):
        if self.es.indices.exists(index=index_name):
            self.es.indices.delete(index=index_name) 
            print('인덱스 삭제 성공!')
        else:
            print(f"{index_name} 인덱스 존재하지 않음")

    def add_documents(self, index_name, df):
        actions = [
            {
                "_index": index_name,
                "_id": row["pk"],
                "_source": {**row.drop("pk").to_dict(), "text_vec": row["text_vec"], "image_vec": row["image_vec"].tolist()}
            }
            for _, row in df.iterrows()
        ]
        
        for i in range(0, len(actions), 500):
            batch = actions[i:i + 500]
            helpers.bulk(self.es, batch)
            print(f'{i + len(batch)}개의 데이터 삽입 성공!')


def upload_to_elasticsearch(es_manager, index_name, df):
    start_time = time.time()
    if not es_manager.index_exists(index_name):
        es_manager.create_index(index_name)
    es_manager.add_documents(index_name, df)
    end_time = time.time()
    return f"Elasticsearch {index_name}에 데이터 성공적으로 넣었습니다.\n걸린 시간 : {end_time - start_time}"