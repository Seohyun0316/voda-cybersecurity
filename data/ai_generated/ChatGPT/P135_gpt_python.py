import hashlib
import os
import sqlite3


# 비밀번호 해싱 함수
def hash_password(password, salt=None):

    if salt is None:
        salt = os.urandom(16)


    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000
    )


    return salt.hex(), hashed.hex()



# DB 저장
def save_user(username, password):

    salt, hashed_password = hash_password(password)


    conn = sqlite3.connect("user.db")
    cursor = conn.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password_hash TEXT,
            salt TEXT
        )
    """)


    cursor.execute("""
        INSERT INTO users
        (username, password_hash, salt)
        VALUES (?, ?, ?)
    """,
    (
        username,
        hashed_password,
        salt
    ))


    conn.commit()
    conn.close()


    print("회원 저장 완료")



# 테스트
save_user(
    "admin",
    "1234"
)