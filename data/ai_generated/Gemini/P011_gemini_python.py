# 라이브러리 설치 필요: pip install bcrypt
import bcrypt

# 회원가입 시: 비밀번호 해싱(암호화) 후 DB 저장
def register_user(plain_password: str):
    # 비밀번호 문자열을 바이트(bytes)로 변환해야 합니다.
    password_bytes = plain_password.encode('utf-8')
    
    # Salt 생성 및 해싱
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    # DB에는 문자열 형태로 저장하는 것이 편하므로 decode해서 반환합니다.
    # 예: INSERT INTO users (username, password) VALUES ('user123', hashed_password_str);
    return hashed_password.decode('utf-8')

# 로그인 시: 입력한 비밀번호와 DB에 저장된 암호화 비밀번호 비교
def login_user(plain_password: str, hashed_password_from_db: str):
    password_bytes = plain_password.encode('utf-8')
    db_password_bytes = hashed_password_from_db.encode('utf-8')
    
    # 두 비밀번호가 일치하는지 확인
    if bcrypt.checkpw(password_bytes, db_password_bytes):
        print("로그인 성공!")
        return True
    else:
        print("비밀번호가 일치하지 않습니다.")
        return False

# --- 사용 예시 ---
user_password = "mySecurePassword123"

# 1. 회원가입 (DB에 저장할 암호화된 문자열 획득)
saved_db_password = register_user(user_password)
print(f"DB에 저장될 값: {saved_db_password}")

# 2. 로그인 검증
login_user("mySecurePassword123", saved_db_password)  # 성공
login_user("wrong_password", saved_db_password)       # 실패