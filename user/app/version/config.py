def aws_config():
    aws_access_key_id = "AKIAWZMQVI3Z3OR5Z6FY"
    aws_secret_access_key = "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"
    return aws_access_key_id, aws_secret_access_key

def openai():
    openai_key = "sk-proj-3JUo4EwKOKPcoterMJVST3BlbkFJlrgUmwrvlEKN9Nlv3uik"
    return openai_key


BUCKET_SETTING = {
    'bucket_name': 'big7-similarity-bucket',  #'big7-high-manage-sys',
    'region': 'ap-northeast-2'  #'us-west-2'
}

DB_SETTING = {
    'host': '3.38.174.231',
    'user': 'root',
    'password': 'mariadb',
    'database': 'test',
    'port': 3306  
}

ELASTIC_SETTING = {
    'host': '3.38.174.231',
    'port': 9200,
    'scheme': 'http',
    'username': 'elastic',
    'password': 'elastic'
}