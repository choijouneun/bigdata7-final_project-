from dotenv import load_dotenv
import os, re
import boto3
import logging
from botocore.exceptions import ClientError

load_dotenv()

class AWSBoto3():
    def __init__(self):
        self.access_key = os.getenv("Acess_key")
        self.secret_access_key = os.getenv("Secret_access_key")
        # boto3를 사용하여 S3 클라이언트를 생성합니다.
        self.s3_client = boto3.client('s3', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_access_key)
    
    def upload_files(self, bucket_name, folder_path, s3_base_path):
        success_count = 0
        failure_count = 0

        # 지정된 폴더 내의 모든 파일 경로 수집
        file_paths = self.collect_pdf_files(folder_path)
        for file_path in file_paths:
            try:
                # 파일 이름에서 연도, 학년, 월, 과목을 추출
                subject, grade, year, month = self.extract_file_info(file_path)
                
                if year and grade and month and subject:
                    # 과목 이름에서 앞의 3글자만 사용 - 과목 이름에 따라 변경
                    subject = subject[:4]
                    # S3에 업로드될 경로 설정
                    # 파일 형태에 따라 month 다음 변경
                    s3_key = f"{s3_base_path}/{subject}/grade{grade}/{year}/{month}/origin_pdf/{os.path.basename(file_path)}"

                    # S3에 파일 업로드
                    with open(file_path, 'rb') as f:
                        self.s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=f)
                    # 파일 업로드 성공 시 메시지 출력
                    print(f"파일 '{file_path}'을(를) 버킷 '{bucket_name}'의 경로 '{s3_key}'에 성공적으로 업로드했습니다.")
                    
                    success_count += 1
                    logging.info(f"파일 '{file_path}'을(를) 버킷 '{bucket_name}'의 경로 '{s3_key}'에 성공적으로 업로드했습니다.")
                else:
                    logging.error(f"파일 '{file_path}'에서 필요한 정보를 모두 추출할 수 없습니다.")
                    failure_count += 1
            
            except ClientError as e:
                failure_count += 1
                logging.error(f"파일 '{file_path}'을(를) 버킷 '{bucket_name}'에 업로드하는 중 에러가 발생했습니다: {e}")
        
        return success_count, failure_count

    def collect_pdf_files(self, folder_path):
        # 파일형태 변경
        """지정된 폴더 내의 모든 PDF 파일 경로를 수집합니다."""
        pdf_files = []
        for root, _, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".pdf"):
                    pdf_files.append(os.path.join(root, file))
        return pdf_files

    def extract_file_info(self, file_path):
        """파일 이름에서 연도(year), 학년(grade), 월(month), 과목(subject) 정보를 추출합니다."""
        file_name = os.path.basename(file_path)

        # 패턴 1: 2019_G3_11_KOR.pdf
        pattern1 = r'(\d{4})_G(\d+)_(\d+)_(\w+)\.pdf'
        match1 = re.search(pattern1, file_name)

        if match1:
            logging.info(f"패턴 1 일치: {file_name}")
            year = match1.group(1)
            grade = match1.group(2)
            month = match1.group(3)
            subject = match1.group(4)
            return subject, grade, year, month
        else:
            # 패턴 2: 2021_G3_03_KOR_speech_writing.pdf
            pattern2 = r'(\d{4})_G(\d+)_(\d+)_([\w_]+)\.pdf'
            match2 = re.search(pattern2, file_name)
            if match2:
                logging.info(f"패턴 2 일치: {file_name}")
                year = match2.group(1)
                grade = match2.group(2)
                month = match2.group(3)
                subject = match2.group(4)
                return subject, grade, year, month
        
        logging.error(f"파일 이름이 패턴과 일치하지 않습니다: {file_name}")
        return None, None, None, None

if __name__ == "__main__":
    AWSboto3 = AWSBoto3()

    # 예시로 사용할 로컬 폴더 경로와 S3 버킷 이름 설정
    # folder_path 경로 변경 / s3_base_path 경로 변경
    folder_path = r'C:\Users\BIG3-06\Documents\KDT_Bigdata_7\0614-0726_Final_project\preprocessing\MATH\G3'
    bucket_name = 'big7-high-manage-sys'
    s3_base_path = 'workbook2'

    # bucket_name = 'big7-question-genie-bucket'
    # s3_base_path = 'workbook'
    success_count, failure_count = AWSboto3.upload_files(bucket_name, folder_path, s3_base_path)
    
    print(f"파일 업로드 결과:")
    print(f"성공적으로 업로드된 파일 수: {success_count}")
    print(f"업로드 실패한 파일 수: {failure_count}")