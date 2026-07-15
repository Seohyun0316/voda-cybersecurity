"""
P002 - 아이디/비밀번호 로그인 (SQLite 사용)
DB: SQLite — 파일 하나로 동작하는 가장 간단한 DB
"""

import sqlite3
import hashlib

DB_FILE = "users.db"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
    """DB와 테이블 초기화"""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def login(username, password):
    conn = sqlite3.connect(DB_FILE)
    row = conn.execute(
        "SELECT password FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()

    if row and row[0] == hash_password(password):
        print("✅ 로그인 성공!")
    else:
        print("❌ 아이디 또는 비밀번호가 틀렸습니다.")


if __name__ == "__main__":
    init_db()
    username = input("아이디: ")
    password = input("비밀번호: ")
    login(username, password)
