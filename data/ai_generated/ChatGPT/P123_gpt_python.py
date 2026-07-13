import bcrypt

def hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        hashed.encode("utf-8")
    )

# 예시
password = "MySecurePassword123!"

hashed = hash_password(password)
print("저장할 해시:", hashed)

print(verify_password("MySecurePassword123!", hashed))  # True
print(verify_password("wrongpassword", hashed))         # False