import hashlib
import secrets

def hash_password(password: str) -> str:
    # 1. 안전한 랜덤 솔트 생성 (16바이트)
    salt = secrets.token_bytes(16)
    
    # 2. PBKDF2 해싱 (10만 번 반복, sha256 방식)
    iterations = 100000
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations)
    
    # 3. DB 저장을 위해 솔트와 해시를 16진수 문자열로 변환 후 구분자(:)로 결합
    return f"{salt.hex()}:{dk.hex()}"

def verify_password(input_password: str, stored_value: str) -> bool:
    # DB에서 솔트와 해시 분리
    salt_hex, original_hash_hex = stored_value.split(':')
    salt = bytes.fromhex(salt_hex)
    
    # 입력받은 비밀번호를 동일한 조건으로 해싱
    iterations = 100000
    dk = hashlib.pbkdf2_hmac('sha256', input_password.encode('utf-8'), salt, iterations)
    
    # 해시값 비교
    return dk.hex() == original_hash_hex

# 사용 예시
stored_db = hash_password("mySecurePass!")
print("DB 저장용:", stored_db)

print("로그인 성공?", verify_password("mySecurePass!", stored_db)) # True
print("로그인 성공?", verify_password("wrong_pass", stored_db))    # False