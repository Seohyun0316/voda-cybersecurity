import hashlib

def generate_file_checksum(file_path):
    # 가장 간단하고 대중적인 MD5 해시 객체 생성
    hash_md5 = hashlib.md5()
    
    try:
        # 파일을 바이너리 읽기(rb) 모드로 오픈
        with open(file_path, "rb") as f:
            # 대용량 파일을 고려해 4096 바이트씩 나누어 읽기
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        # 16진수 문자열로 체크섬 반환
        return hash_md5.hexdigest()
    
    except FileNotFoundError:
        return "파일을 찾을 수 없습니다. 경로를 확인해주세요."

# ─── 사용 예시 ───
# 'test.txt' 자리에 체크섬을 구하고 싶은 파일 경로를 넣으세요.
file_name = "test.txt" 
checksum = generate_file_checksum(file_name)

print(f"파일 이름: {file_name}")
print(f"MD5 체크섬: {checksum}")