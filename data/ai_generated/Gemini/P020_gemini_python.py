import bcrypt

# 임시 사용자 데이터베이스 (실제로는 실제 DB를 사용하게 됩니다)
user_db = {}

def register_user(email, password):
    # 1. 입력받은 문자열 비밀번호를 바이트(bytes) 형태로 변환합니다.
    password_bytes = password.encode('utf-8')
    
    # 2. 솔트(Salt)를 생성하고 비밀번호를 암호화(해싱)합니다.
    # bcrypt.gensalt()가 자동으로 강력한 솔트를 만들어 줍니다.
    hashed_password = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    
    # 3. 암호화된 비밀번호를 DB에 저장합니다. (바이트 그대로 저장하거나 디코딩하여 문자열로 저장)
    user_db[email] = hashed_password.decode('utf-8')
    
    print(f"[{email}] 회원가입 성공!")
    print(f"DB에 저장된 비밀번호 형태: {user_db[email]}\n")


# --- 실제 작동 테스트 ---
# 1. 회원가입 진행
register_user("user@example.com", "my_secure_password123!")