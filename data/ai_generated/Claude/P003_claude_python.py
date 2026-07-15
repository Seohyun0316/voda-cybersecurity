"""
P003 - 회원가입 (SQLite, 비밀번호 해시 저장)
비밀번호는 SHA-256으로 암호화 후 저장 — 평문 저장 절대 금지
"""

import sqlite3
import hashlib

DB_FILE = "users.db"


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def init_db():
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


def signup(username, password):
    conn = sqlite3.connect(DB_FILE)
    try:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_password(password))
        )
        conn.commit()
        print("✅ 회원가입 완료!")
    except sqlite3.IntegrityError:
        print("❌ 이미 존재하는 아이디입니다.")
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    username = input("아이디: ")
    password = input("비밀번호: ")
    signup(username, password)
