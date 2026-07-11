import secrets

def create_reset_token():
    """비밀번호 재설정용 임시 토큰 생성 함수"""
    return secrets.token_hex(32)

# 사용 예시
token = create_reset_token()
print(token)
# 출력 예시: e7b3c1a9... (64글자의 랜덤 문자열)