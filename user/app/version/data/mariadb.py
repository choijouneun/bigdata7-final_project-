import time
import pymysql
import sys
sys.path.append('/app/version')
from config import DB_SETTING
from model.similarity import fetch_all_docs, find_similar_docs

class MariaDBManager:
    """
    MariaDB를 관리하는 클래스
    - create_table : 테이블 생성
    - delete_table : 테이블 삭제
    - insert_data : 데이터 삽입
    """
    def __init__(self):
        self.connection = pymysql.connect(
            host=DB_SETTING['host'], 
            user=DB_SETTING['user'], 
            password=DB_SETTING['password'], 
            database=DB_SETTING['database'],
            port=DB_SETTING['port']
        )

    def disconnect(self):
        if self.connection:
            self.connection.close()

    def execute_query(self, query):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
            self.connection.commit()
        except pymysql.MySQLError as e:
            print(f"Error: {e}")

    def fetchone_query(self, query):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchone()
            return result
        except pymysql.MySQLError as e:
            print(f"Error: {e}")
            return None

    def table_exists(self, table_name):
        exist_sql = f"SHOW TABLES LIKE '{table_name}';"
        result = self.fetchone_query(exist_sql)
        return result is not None

    def delete_table(self, table_name):
        drop_sql = f"DROP TABLE IF EXISTS {table_name};"
        self.execute_query(drop_sql)
    
    def clear_table(self, table_name):
        clear_sql = f"DELETE FROM {table_name};"
        self.execute_query(clear_sql)
        self.connection.commit()

    # 데이터 입력
    def insert_data(self, table_name, df):
        for _, row in df.iterrows():
            keys = ", ".join(row.index)
            values = ", ".join([
                "'{}'".format(value.replace("'", "''")) if isinstance(value, str) and value != '' else 'NULL' if value == '' else str(value)
                for value in row.values
            ])
            insert_sql = f"INSERT INTO {table_name} ({keys}) VALUES ({values});"
            try:
                self.execute_query(insert_sql)
            except Exception as e:
                print(f"Error: {e}")

    # 문항 테이블 생성
    def create_questions_table(self, table_name):
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                pk VARCHAR(20) PRIMARY KEY,
                grade INT NOT NULL,
                yyyy YEAR NOT NULL,
                mm INT NOT NULL,
                host INT NOT NULL,
                subject_cat INT NOT NULL,
                question_cat TEXT,
                question_num INT NOT NULL,
                points INT,
                text_title TEXT,
                text TEXT,
                text_yn INT,
                question TEXT,
                paragraph TEXT,
                choice1 TEXT,
                choice2 TEXT,
                choice3 TEXT,
                choice4 TEXT,
                choice5 TEXT,
                short_answer INT,
                multiple_answer INT,
                text_exp TEXT,
                question_exp TEXT
            );
        """
        self.execute_query(create_sql)

    # 풀이이력 테이블 생성 
    def create_solution_tables(self, table_name):
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                userid VARCHAR(50),
                round INT,
                input_1 INT,
                input_2 INT,
                input_3 INT,
                input_4 INT,
                input_5 INT,
                correct_1 BOOLEAN,
                correct_2 BOOLEAN,
                correct_3 BOOLEAN,
                correct_4 BOOLEAN,
                correct_5 BOOLEAN,
                score INT
            );
        """
        self.execute_query(create_sql)

    # 랜덤문제 메타정보 테이블 생성
    def create_meta_tables(self, table_name):
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                round INT PRIMARY KEY,
                question1 VARCHAR(20),
                question2 VARCHAR(20),
                question3 VARCHAR(20),
                question4 VARCHAR(20),
                question5 VARCHAR(20)
            );
        """
        self.execute_query(create_sql)

    # 유사도 쌍 테이블 생성
    def create_similarity_table(self, table_name):
        create_sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                origin_id VARCHAR(20),
                similarity_id VARCHAR(20),
                similarity_value FLOAT
            )
            """
        self.execute_query(create_sql)

    # # 사용자 입력 유사도 쌍 테이블 생성
    # def create_user_table(self, table_name):
    #     create_sql = f"""
    #         CREATE TABLE IF NOT EXISTS {table_name} (
    #             question_id VARCHAR(20),
    #             directory VARCHAR(100),
    #             similarity_id VARCHAR(20),
    #             similarity_value FLOAT
    #         )
    #         """
    #     self.execute_query(create_sql)


def upload_questions_data(db_manager, table_name, df):
    if not db_manager.table_exists(table_name):
        db_manager.create_questions_table(table_name)
    db_manager.insert_data(table_name, df)
    return f"Mariadb {table_name}에 데이터 성공적으로 넣었습니다."

def upload_similarity_data(db_manager, index_name, sim_table_name, subject):
    sim_start_time = time.time()
    all_docs = fetch_all_docs(index_name)
    similarity_df = find_similar_docs(index_name, all_docs, subject)
    similarity_df = similarity_df.sort_values(by=['origin_id', 'similarity_value'], ascending=[True, False]).reset_index(drop=True)

    if not db_manager.table_exists(sim_table_name):
        db_manager.create_similarity_table(sim_table_name)
    else:
        db_manager.clear_table(sim_table_name)

    db_manager.insert_data(sim_table_name, similarity_df)
    sim_end_time = time.time()
    return f"Mariadb {sim_table_name}에 데이터 성공적으로 넣었습니다.\n걸린 시간 : {sim_end_time - sim_start_time}"

# def upload_user_data(db_manager, table_name, df):
#     if not db_manager.table_exists(table_name):
#         db_manager.create_user_table(table_name)
#     db_manager.insert_data(table_name, df)
#     return f"Mariadb {table_name}에 데이터 성공적으로 넣었습니다."