import hashlib

def encrypt_password(password):
    # 비밀번호 문자열을 바이트(bytes)로 인코딩한 뒤 SHA-256 해시를 생성합니다.
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

# 사용 예시
user_password = "my_secret_password123"
encrypted = encrypt_password(user_password)

print(f"원래 비밀번호: {user_password}")
print(f"암호화된 비밀번호: {encrypted}")