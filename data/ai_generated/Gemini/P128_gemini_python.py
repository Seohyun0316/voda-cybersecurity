import secrets

def generate_invite_code(length=12):
    # URL에 안전한 베이스64 문자열 생성 (지정한 바이트 수 기준이라 length보다 약간 길어질 수 있음)
    #토큰 길이를 대략 맞추기 위해 바이트 수를 조절합니다.
    return secrets.token_urlsafe(length)[:length]

# 초대 코드 생성 (예: 12자리)
invite_code = generate_invite_code(12)
print(f"초대 코드: {invite_code}")
print(f"초대 링크 예시: https://your-service.com/join?code={invite_code}")