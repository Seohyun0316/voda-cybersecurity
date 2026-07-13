import bcrypt

# 1. 비밀번호 암호화 (회원가입 시 사용)
def hash_password(plain_password: str) -> bytes:
    # 암호화할 비밀번호를 바이트 형태로 변환
    password_bytes = plain_password.encode('utf-8')
    
    # 솔트(Salt) 생성 및 해싱 (기본 작업량은 12로 설정됨)
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    return hashed_password

# 2. 비밀번호 검증 (로그인 시 사용)
def compare_password(plain_password: str, hashed_password: bytes) -> bool:
    # 입력받은 비밀번호를 바이트 형태로 변환
    password_bytes = plain_password.encode('utf-8')
    
    # DB에 저장된 암호화 값과 비교
    is_match = bcrypt.checkpw(password_bytes, hashed_password)
    return is_match


# --- 실행 예시 ---
if __name__ == "__main__":
    my_password = "mySecretPassword123!"
    print(f"원본 비밀번호: {my_password}")

    # 회원가입: 암호화해서 DB에 저장할 값 생성
    db_stored_password = hash_password(my_password)
    print(f"DB에 저장될 암호화된 값: {db_stored_password}")

    print("\n--- 로그인 시도 ---")

    # 로그인 성공 케이스
    is_login_success = compare_password("mySecretPassword123!", db_stored_password)
    print(f"맞는 비밀번호 입력 시 결과: {is_login_success}")  # True

    # 로그인 실패 케이스
    is_login_fail = compare_password("wrongPassword", db_stored_password)
    print(f"틀린 비밀번호 입력 시 결과: {is_login_fail}")  # False