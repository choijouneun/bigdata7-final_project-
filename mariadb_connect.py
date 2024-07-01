import json
import pymysql

# MariaDB 연결 설정
connection = pymysql.connect(
    host='localhost',  # 호스트 주소
    user='root',  # MariaDB 사용자
    password='mariadb',  # MariaDB 비밀번호
    database='manage_sys',  # 데이터베이스 이름
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

# JSON 파일 읽기
with open('./2019 고3 3월 국어.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 데이터 삽입 함수
def insert_data(cursor, record):
    grade = record['grade']
    yyyy = record['yyyy']
    mm = f"{record['mm']:02d}"  # mm이 한자리 숫자이면 앞에 0 추가
    subject_cat = f"{record['subject_cat']:02d}"  # subject_cat이 한자리 숫자이면 앞에 0 추가
    question_num = record['question_num']
    
    # pk 생성
    pk = f"G{grade}{yyyy}{mm}{subject_cat}Q{question_num}"

    # multiple_answer 값 처리
    multiple_answer = record.get('multiple_answer', 0)
    if multiple_answer == '' or multiple_answer is None:
        multiple_answer = 0
    else:
        multiple_answer = int(multiple_answer)
    
    sql = """
    INSERT INTO questions_korean (pk, grade, yyyy, mm, host, subject_cat, question_cat, question_num, points, text_title, text_yn, text, question, paragraph, choice1, choice2, choice3, choice4, choice5, multiple_answer, short_answer, explanation)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(sql, (
        pk,
        record['grade'],
        record['yyyy'],
        record['mm'],
        record['host'],
        record['subject_cat'],
        '',  # question_cat 데이터가 없으므로 빈 문자열로 설정
        record['question_num'],
        record['points'],
        record['text_title'],
        record['text_yn'],
        record['text'],
        record['question'],
        record.get('paragraph', ''),  # paragraph가 없으면 빈 문자열
        record['choice1'],
        record['choice2'],
        record['choice3'],
        record['choice4'],
        record['choice5'],
        multiple_answer,  # 처리된 multiple_answer 값
        record.get('short_answer', ''),  # short_answer가 없으면 빈 문자열
        ''  # explanation 데이터가 없으므로 빈 문자열로 설정
    ))

# 데이터베이스에 데이터 삽입
try:
    with connection.cursor() as cursor:
        for record in data:
            insert_data(cursor, record)
    connection.commit()
finally:
    connection.close()
