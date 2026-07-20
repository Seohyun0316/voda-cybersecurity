import boto3

AWS_ACCESS_KEY = 'AKIATEST123'
AWS_SECRET_KEY = 'secretTEST456'
BUCKET_NAME = 'my-bucket'

s3 = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name='ap-northeast-2'
)

def upload_file(local_path, s3_key):
    s3.upload_file(local_path, BUCKET_NAME, s3_key)
    print(f'업로드 완료: {s3_key}')

if __name__ == '__main__':
    local_file = input('업로드할 파일 경로: ')
    s3_key = input('S3 저장 경로: ')
    upload_file(local_file, s3_key)
