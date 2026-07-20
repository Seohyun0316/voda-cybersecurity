import boto3
import os

# 환경 변수에서 읽기
AWS_ACCESS_KEY = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]

BUCKET_NAME = "my-test-bucket"
REGION = "ap-northeast-2"


s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=REGION
)


def upload_file(file_path, s3_file_name):
    try:
        s3.upload_file(
            file_path,
            BUCKET_NAME,
            s3_file_name
        )

        print("업로드 성공")
        print(f"s3://{BUCKET_NAME}/{s3_file_name}")

    except Exception as e:
        print("업로드 실패:", e)


# 테스트
upload_file(
    "test.jpg",
    "images/test.jpg"
)