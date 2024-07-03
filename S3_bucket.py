from dotenv import load_dotenv
import os
import boto3
import logging
from botocore.exceptions import ClientError

load_dotenv()

# 환경 변수 사용
# aws_id = os.getenv("Acess_key")
# aws_password = os.getenv("Secret_access_key")
# aws_bucket = boto3.client('')

# print(f"Acess_key ID: {aws_id}")
# print(f"Database Secret_access_key: {aws_password}")

class AWSBoto3():
    def __init__(self):
        self.access_key = os.getenv("Acess_key")
        self.secret_access_key = os.getenv("Secret_access_key")
        # boto3를 사용하여 S3 클라이언트를 생성합니다.
        self.s3_client = boto3.client('s3', aws_access_key_id=self.access_key, aws_secret_access_key=self.secret_access_key)
            

    def create_bucket(self, bucket_name, region='ap-northeast-2'):
    # def create_bucket(self, bucket_name, region='us-west-2'):
        """지정된 지역에 S3 버킷을 생성합니다.
        
        지역이 지정되지 않으면 기본 지역(us-east-1)에 버킷이 생성됩니다.

        :param bucket_name: 생성할 버킷 이름
        :param region: 버킷을 생성할 지역의 문자열, 예: 'us-west-2'
        :return: 버킷이 생성되면 True, 그렇지 않으면 False
        """

        # Create bucket
        try:
            # 버킷이 이미 존재하는지 확인
            response = self.s3_client.head_bucket(Bucket=bucket_name)
            logging.warning(f'Bucket "{bucket_name}" already exists.')
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # 버킷이 없는 경우 생성
                location = {'LocationConstraint': region}
                try:
                    self.s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
                except ClientError as e:
                    logging.error(e)
                    return False
                return True
            else:
                logging.error(e)
                return False
    
    def create_folders(self, bucket_name, folder_list):
        """지정된 버킷에 여러 폴더를 생성합니다."""
        try:
            for folder in folder_list:
                # 각 폴더를 생성하기 위해 폴더 경로로 빈 객체를 업로드합니다.
                self.s3_client.put_object(Bucket=bucket_name, Key=(folder + '/'))
        except ClientError as e:
            logging.error(f"폴더 '{folder}' 생성에 실패했습니다. 에러: {e}")
            return False
        return True


if __name__ == "__main__":
    # AWSBoto3 클래스의 인스턴스를 생성합니다.
    AWSboto3 = AWSBoto3()
    # 예시 버킷 이름으로 버킷을 생성해봅니다. 실제 실행 시 버킷 이름을 적절히 변경하세요.
    bucket_name = 'big7-question-genie-bucket'
    success = AWSboto3.create_bucket(bucket_name)
    if success:
        print(f"버킷 '{bucket_name}'이(가) 성공적으로 생성되었습니다.")
    else:
        print(f"버킷 '{bucket_name}' 생성에 실패했습니다.")


    # 폴더 경로 생성
    cats = ["workbook", "answer"]
    subjects = ["KOR", "ENG", "MATH"]
    grade1_2_years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    grade1_2_months = ["03", "06", "09", "11"]

    grade3_years = [2019, 2020, 2021, 2022, 2023, 2024]
    grade3_months = ["03", "04", "06", "07", "09", "10", "11"]
        
    folder_list = []

    # G1, G2에 대한 폴더 생성
    for cat in cats:
        for subject in subjects:
            for grade in [1,2]:
                for year in grade1_2_years:
                    for month in grade1_2_months:
                        origin_pdf_path = f'{cat}/{subject}/grade{grade}/{year}/{month}/origin_pdf'
                        text_path = f'{cat}/{subject}/grade{grade}/{year}/{month}/text'
                        full_image_path = f'{cat}/{subject}/grade{grade}/{year}/{month}/image/full_image'
                        only_image_path = f'{cat}/{subject}/grade{grade}/{year}/{month}/image/only_image'
                        
                        if not AWSboto3.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=origin_pdf_path)['KeyCount']:
                            folder_list.append(origin_pdf_path)
                        if not AWSboto3.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=text_path)['KeyCount']:
                            folder_list.append(text_path)
                        if not AWSboto3.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=full_image_path)['KeyCount']:
                            folder_list.append(full_image_path)
                        if not AWSboto3.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=only_image_path)['KeyCount']:
                            folder_list.append(only_image_path)

    # G3에 대한 폴더 생성
    for cat in cats:
        for subject in subjects:
            for grade in [3]:
                for year in grade3_years:
                    for month in grade3_months:
                            origin_pdf_path = f'{cat}/{subject}/grade{grade}/{year}/{month}/origin_pdf'
                            text_path = f'{cat}/{subject}/grade{grade}/{year}/{month}/text'
                            full_image_path = f'{cat}/{subject}/grade{grade}/{year}/{month}/image/full_image'
                            only_image_path = f'{cat}/{subject}/grade{grade}/{year}/{month}/image/only_image'
                            
                            if not AWSboto3.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=origin_pdf_path)['KeyCount']:
                                folder_list.append(origin_pdf_path)
                            if not AWSboto3.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=text_path)['KeyCount']:
                                folder_list.append(text_path)
                            if not AWSboto3.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=full_image_path)['KeyCount']:
                                folder_list.append(full_image_path)
                            if not AWSboto3.s3_client.list_objects_v2(Bucket=bucket_name, Prefix=only_image_path)['KeyCount']:
                                folder_list.append(only_image_path)

    if AWSboto3.create_folders(bucket_name, folder_list):
        print(f"폴더들이 버킷 '{bucket_name}'에 성공적으로 생성되었습니다.")
    else:
        print(f"폴더 생성에 실패했습니다.")