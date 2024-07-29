import sys
from utils.config import aws_config
import pandas as pd
import boto3
import json
from PIL import Image


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