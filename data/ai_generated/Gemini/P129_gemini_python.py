import bcrypt

# 1. 비밀번호 해싱 (회원가입 시 사용)
def hash_password(plain_password: str) -> str:
    # bcrypt는 바이트 문자열을 입력받으므로 encode()가 필요합니다.
    password_bytes = plain_password.encode('utf-8')
    
    # 자동으로 솔트(Salt)를 생성하고 해싱을 진행합니다.
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    
    # DB에 저장하기 편하도록 문자열(str)로 변환하여 반환합니다.
    return hashed_bytes.decode('utf-8')

# 2. 비밀번호 검증 (로그인 시 사용)
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    # 입력한 비밀번호가 기존 해시와 일치하는지 비교합니다.
    return bcrypt.checkpw(password_bytes, hashed_bytes)

# --- 사용 예시 ---
raw_password = "my_secure_password123"

# 회원가입 시 DB에 저장할 해시값 생성
db_password = hash_password(raw_password)
print(f"DB에 저장될 해시: {db_password}")

# 로그인 시도 검증
is_match = verify_password("my_secure_password123", db_password)
print(f"로그인 성공 여부: {is_match}")  # True