import bcrypt

def hash_password(password: str) -> bytes:
    """
    사용자가 입력한 평문 비밀번호를 해싱합니다.
    """
    # 1. 비밀번호 문자열을 바이트(bytes) 형태로 인코딩합니다.
    password_bytes = password.encode('utf-8')
    
    # 2. 솔트(Salt)를 생성합니다. (기본 워크 팩터는 12로 설정되어 보안성이 높습니다)
    salt = bcrypt.gensalt()
    
    # 3. 비밀번호와 솔트를 조합하여 해시를 생성합니다.
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    return hashed_password

def check_password(password: str, hashed_password: bytes) -> bool:
    """
    사용자가 입력한 평문 비밀번호와 DB에 저장된 해시 값을 비교하여 일치하는지 확인합니다.
    """
    password_bytes = password.encode('utf-8')
    
    # bcrypt.checkpw가 알아서 해시 값 내부의 솔트를 추출해 비교해 줍니다.
    return bcrypt.checkpw(password_bytes, hashed_password)

# --- 사용 예시 ---
if __name__ == "__main__":
    user_password = "my_secure_password123!"
    
    # 1. 회원가입 시: 비밀번호 해싱 후 DB 저장
    db_stored_hash = hash_password(user_password)
    print(f"해싱된 비밀번호 (DB 저장용): {db_stored_hash.decode('utf-8')}\n")
    
    # 2. 로그인 시: 비밀번호 검증
    login_attempt_1 = "my_secure_password123!"
    login_attempt_2 = "wrong_password"
    
    print(f"맞는 비밀번호 입력 시 결과: {check_password(login_attempt_1, db_stored_hash)}") # True
    print(f"틀린 비밀번호 입력 시 결과: {check_password(login_attempt_2, db_stored_hash)}") # False