import bcrypt


# 비밀번호 해싱 함수
def hash_password(password):
    # 문자열 → 바이트 변환
    password_bytes = password.encode("utf-8")

    # salt 생성 + 해싱
    hashed_password = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed_password


# 비밀번호 검증 함수
def check_password(password, hashed_password):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed_password
    )


# 회원가입 예시
password = "1234"

hashed = hash_password(password)

print("원래 비밀번호:", password)
print("DB 저장용 해시:", hashed)


# 로그인 예시
login_password = "1234"

if check_password(login_password, hashed):
    print("로그인 성공")
else:
    print("비밀번호 불일치")_password))