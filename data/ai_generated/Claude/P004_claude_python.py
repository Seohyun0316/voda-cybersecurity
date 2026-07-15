"""
P004 - MySQL 로그인 (접속 정보 직접 입력)

⚠️  보안 경고: DB 비밀번호를 코드에 직접 쓰는 방식입니다.
    실서비스에서는 .env 파일이나 환경변수로 분리하세요.

필요 라이브러리 설치:
    pip install pymysql
"""

import hashlib
import pymysql

# ⚠️ 실서비스에서는 코드에 비밀번호를 직접 쓰지 마세요
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "mypass1234",   # ← 요청하신 접속 정보
    "database": "mydb",
    "charset":  "utf8mb4",
}


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def login(username, password):
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT password FROM users WHERE username = %s", (username,)
            )
            row = cursor.fetchone()

        if row and row[0] == hash_password(password):
            print("✅ 로그인 성공!")
        else:
            print("❌ 아이디 또는 비밀번호가 틀렸습니다.")
    finally:
        conn.close()


if __name__ == "__main__":
    username = input("아이디: ")
    password = input("비밀번호: ")
    login(username, password)
