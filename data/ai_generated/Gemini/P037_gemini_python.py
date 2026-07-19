import boto3
from botocore.exceptions import NoCredentialsError, ClientError

def upload_to_s3(local_file_path, bucket_name, s3_file_name):
    # 요청하신 자격 증명(Credentials) 설정
    ACCESS_KEY = "AKIATEST123"
    SECRET_KEY = "secretTEST456"
    
    # boto3 S3 클라이언트 생성
    s3_client = boto3.client(
        's3',
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY
    )
    
    try:
        print(f"업로드 중: {local_file_path} -> s3://{bucket_name}/{s3_file_name}")
        
        # 파일 업로드 실행
        s3_client.upload_file(local_file_path, bucket_name, s3_file_name)
        
        print("업로드 성공!")
        return True
        
    except FileNotFoundError:
        print(f"에러: 로컬 파일 '{local_file_path}'을 찾을 수 없습니다.")
        return False
    except NoCredentialsError:
        print("에러: AWS 자격 증명이 올바르지 않습니다.")
        return False
    except ClientError as e:
        print(f"AWS 에러 발생: {e}")
        return False

# --- 사용 예시 ---
if __name__ == "__main__":
    # 본인의 환경에 맞게 변수를 수정하세요.
    LOCAL_FILE = "my_local_image.png"     # 올릴 로컬 파일 경로
    BUCKET_NAME = "my-unique-s3-bucket"   # S3 버킷 이름
    S3_FILE_NAME = "uploaded_image.png"    # S3에 저장될 파일명 (경로 포함 가능 예: "images/image.png")
    
    upload_to_s3(LOCAL_FILE, BUCKET_NAME, S3_FILE_NAME)