import os, itertools, boto3, logging, re, time
from botocore.exceptions import ClientError
import pandas as pd
import json
from PIL import Image
import sys
sys.path.append('/app/version')
from config import aws_config

# 로그 설정
log_file = 'preprocessing_main.log'
logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(log_file), logging.StreamHandler()])


class S3BucketManager:
    def __init__(self, bucket_name, region):
        self.access_key, self.secret_access_key = aws_config()
        self.s3_client = boto3.client('s3', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_access_key)
        self.bucket_name = bucket_name
        self.region = region
            
    def create_bucket(self):
        """
        S3 버킷 생성
        return: 버킷이 생성되면 True, 그렇지 않으면 False
        """
        logging.info(f"Checking if bucket '{self.bucket_name}' exists.")
        
        try:
            # 버킷이 이미 존재하는지 확인
            response = self.s3_client.head_bucket(Bucket=self.bucket_name)
            logging.warning(f'Bucket "{self.bucket_name}" already exists.')
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':  # 버킷이 없는 경우 생성
                location = {'LocationConstraint': self.region}
                try:
                    self.s3_client.create_bucket(Bucket=self.bucket_name, CreateBucketConfiguration=location)
                    logging.info(f"Bucket '{self.bucket_name}' created successfully.")
                except ClientError as e:
                    logging.error(f"Failed to create bucket '{self.bucket_name}': {e}")
                    return False
                return True
            else:
                logging.error(e)
                return False
    
    def create_folders(self, folder_list):
        """폴더 생성"""
        try:
            for folder in folder_list:
                # 각 폴더를 생성하기 위해 폴더 경로로 빈 객체를 업로드
                self.s3_client.put_object(Bucket=self.bucket_name, Key=(folder + '/'))
                logging.info(f"Folder '{folder}' created in bucket '{self.bucket_name}'.")
        except ClientError as e:
            logging.error(f"Failed to create folder '{folder}'. Error: {e}")
            return False
        return True
    
    def add_folder_if_not_exists(self, folder_path):
        if not self.s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=folder_path)['KeyCount']:
            return folder_path
        return None
    

    def generate_folder_paths(self, cats, subjects, grades, years, months, special_months):
        """폴더 경로 생성"""
        paths = []
        for cat, subject, grade, year in itertools.product(cats, subjects, grades, years):
            months_to_use = special_months if year == 2024 and grade in [1, 2] else months
            for month in months_to_use:
                paths.extend([
                    f'{cat}/{subject}/grade{grade}/{year}/{month}/origin_pdf',
                    f'{cat}/{subject}/grade{grade}/{year}/{month}/text',
                    f'{cat}/{subject}/grade{grade}/{year}/{month}/image'
                ])
        return paths
    

class S3FileUploader:
    def __init__(self, bucket_name):
        self.access_key, self.secret_access_key = aws_config()
        self.s3_client = boto3.client('s3', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_access_key)
        self.bucket_name = bucket_name

    def upload_files(self, base_folder_paths, s3_base_path, answer_path=None):
        success_count = 0
        failure_count = 0

        folder_mapping = {
        'png': os.path.join(base_folder_paths['base'], base_folder_paths['png']) if base_folder_paths['png'] else base_folder_paths['base'],
        'json': os.path.join(base_folder_paths['base'], base_folder_paths['json']),
        'pdf': os.path.join(base_folder_paths['base'], base_folder_paths['pdf'])
        }
        for extension, folder_path in folder_mapping.items():
            file_paths = self.collect_files(folder_path, extension)
            logging.info(f"Collecting {extension} files from {folder_path}. Found {len(file_paths)} files.")
            for file_path in file_paths:
                try:
                    # 파일 이름에서 연도, 학년, 월, 과목을 추출
                    subject, grade, year, month, extension = self.extract_file_info(file_path)
                    if subject and grade and year and month:
                        if extension == "png" and answer_path and answer_path in file_path:
                            s3_key = f"answer/{subject}/grade{grade}/{year}/{month}/image/{os.path.basename(file_path)}"
                        elif extension == "png":
                            s3_key = f"{s3_base_path}/{subject}/grade{grade}/{year}/{month}/image/{os.path.basename(file_path)}"
                        elif extension == "json":
                            s3_key = f"{s3_base_path}/{subject}/grade{grade}/{year}/{month}/text/{os.path.basename(file_path)}"
                        elif extension == "pdf":
                            s3_key = f"{s3_base_path}/{subject}/grade{grade}/{year}/{month}/origin_pdf/{os.path.basename(file_path)}"
                        else:
                            continue
                    
                        # S3에 파일 업로드
                        with open(file_path, 'rb') as f:
                            self.s3_client.put_object(Bucket=self.bucket_name, Key=s3_key, Body=f)
                        # 파일 업로드 성공 시 메시지 출력
                        print(f"Successfully uploaded '{file_path}' to '{self.bucket_name}/{s3_key}'.")
                        success_count += 1
                    else:
                        logging.error(f"Failed to extract info from '{file_path}'.")
                        failure_count += 1       
                except ClientError as e:
                    failure_count += 1
                    logging.error(f"Error uploading '{file_path}' to '{self.bucket_name}': {e}")
            
        return success_count, failure_count

    def collect_files(self, folder_path, extension):
        """파일 수집"""
        files = []
        for root, _, file_names in os.walk(folder_path):
            for file_name in file_names:
                if file_name.endswith(f".{extension}"):
                    files.append(os.path.join(root, file_name))
        return files

    def extract_file_info(self, file_path):
        """파일 이름에서 연도(year), 학년(grade), 월(month), 과목(subject) 정보 추출"""
        file_name = os.path.basename(file_path)

        # 과목 - 학년 - 년도 - 월 - 문항번호(세부과목..)
        pattern = r'(\w+)_G(\d+)_(\d{4})_(\d+)(?:_([\w_]+))?\.(png|json|pdf)'
        match = re.search(pattern, file_name)
        if match:
            logging.info(f"패턴 일치: {file_name}")
            subject = match.group(1)
            grade = match.group(2)
            year = match.group(3)
            month = match.group(4)
            extra_info = match.group(5)  # 그룹 5는 선택적이므로 None일 수 있음
            extension = match.group(6)
            return subject, grade, year, month, extension
        else:
            logging.error(f"파일 이름이 패턴과 일치하지 않습니다: {file_name}")
            return None, None, None, None, None


class S3DataLoader:
    def __init__(self, bucket_name, prefix):
        self.access_key, self.secret_key = aws_config()
        self.s3_client = boto3.client("s3", aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_key)
        self.s3 = boto3.resource('s3')
        self.bucket_name = bucket_name
        self.prefix = prefix

    def list_all_objects(self):
        objects = []
        continuation_token = None

        while True:
            list_kwargs = {'Bucket': self.bucket_name, 'Prefix': self.prefix}
            if continuation_token:
                list_kwargs['ContinuationToken'] = continuation_token

            response = self.s3_client.list_objects_v2(**list_kwargs)
            objects.extend(response.get('Contents', []))

            if not response.get('IsTruncated'):
                break

            continuation_token = response.get('NextContinuationToken')

        return objects

    def read_image_from_s3(self, filename):
        bucket = self.s3.Bucket(self.bucket_name)
        object = bucket.Object(filename)
        response = object.get()
        file_stream = response['Body']
        img = Image.open(file_stream)
        return img

    def read_json_from_s3(self, filename):
        bucket = self.s3.Bucket(self.bucket_name)
        object = bucket.Object(filename)
        response = object.get()
        file_stream = response['Body']
        json_data = json.load(file_stream)
        df = pd.DataFrame(json_data)
        return df
    

def setup_s3(bucket_name, region):
    bucket_manager = S3BucketManager(bucket_name, region)
    bucket_exists = bucket_manager.create_bucket()
    if not bucket_exists:
        create_s3_directories(bucket_manager, bucket_name)

def create_s3_directories(bucket_manager, bucket_name):
    cats = ["workbook", "answer"]
    subjects = ["KOR", "ENG", "MATH"]
    grade1_2_years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    grade1_2_months = ["03", "06", "09", "11"]
    grade3_years = [2019, 2020, 2021, 2022, 2023, 2024]
    grade3_months = ["03", "04", "06", "07", "09", "10", "11"]
    G1_2_special_months = ["03", "06"]
    G3_special_months = ["03", "04", "06"]

    folder_list = []

    folder_paths_1_2 = bucket_manager.generate_folder_paths(cats, subjects, [1, 2], grade1_2_years, grade1_2_months, G1_2_special_months)
    folder_paths_3 = bucket_manager.generate_folder_paths(cats, subjects, [3], grade3_years, grade3_months, G3_special_months)

    for path in folder_paths_1_2 + folder_paths_3:
        result = bucket_manager.add_folder_if_not_exists(bucket_name, path)
        if result:
            folder_list.append(result)

    bucket_manager.create_folders(folder_list)

def find_answer_files(directory):
    answer_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith("_answer"):
                answer_files.append(os.path.join(root, file))
    return answer_files

def upload_files(bucket_name):
    start_time = time.time()
    file_uploader = S3FileUploader(bucket_name)
    base_folder_paths = {
        'base': "/app/temp_pdf",  # 경로 ------------------------------------------------------------
        'png': 'pdf_images',
        'json': '',
        'pdf': ''
    }  
    pdf_dir = "/app/temp_pdf"
    answer_files = find_answer_files(pdf_dir)  # 경로 ------------------------------------------------------------

    for answer_path in answer_files:
        success_count_workbook, failure_count_workbook = file_uploader.upload_files(base_folder_paths, 'workbook')
        success_count_answer, failure_count_answer = file_uploader.upload_files({'base': answer_path, 'png': '', 'json': '', 'pdf': ''}, 'answer')
        end_time = time.time()

    print("File upload results for workbook:")
    print("Number of files successfully uploaded:", success_count_workbook)
    print("Number of files failed to upload:", failure_count_workbook)

    print("File upload results for answer:")
    print("Number of files successfully uploaded:", success_count_answer)
    print("Number of files failed to upload:", failure_count_answer)
    return f"S3에 파일과 데이터 업로드 완료했습니다.\n걸린시간 : {end_time - start_time}"

def get_s3_keys(s3_loader):
    objects = s3_loader.list_all_objects()
    img_key_list = [obj['Key'] for obj in objects if obj['Key'].endswith('.png')]
    text_key_list = [obj['Key'] for obj in objects if obj['Key'].endswith('.json')]
    return img_key_list, text_key_list