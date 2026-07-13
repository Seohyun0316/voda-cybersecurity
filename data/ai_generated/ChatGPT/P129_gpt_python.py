import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def check_password(password, hashed):
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )

# 사용 예시
password = "hello1234"

hashed_password = hash_password(password)

print("저장할 값:")
print(hashed_password)

print("비밀번호 확인:")
print(check_password("hello1234", hashed_password))
print(check_password("wrong", hashed_password))