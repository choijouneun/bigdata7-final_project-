import numpy as np
from elasticsearch import Elasticsearch, helpers

class ElasticManager:
    """
    Elasticsearch 관리하는 클래스
    - es 클라이언트 생성
    - create_index : 인덱스 생성
    - delete_index : 인덱스 삭제
    - add_documents : 데이터 한번에 업로드
    """
    def __init__(self, host, port, scheme, username, password):
        self.es = Elasticsearch(
            [{'host': host, 'port': port, 'scheme': scheme}]
        ).options(basic_auth=(username, password))

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
        helpers.bulk(self.es, actions)
        print('데이터 삽입 성공!')