"""
P006 - 회원가입 + 테스트 계정(admin/admin1234) 미리 삽입

⚠️  보안 경고: 테스트 계정은 개발 환경 전용입니다.
    실서비스 배포 전에 반드시 이 계정을 삭제하거나 비밀번호를 변경하세요.
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
    # ⚠️ 테스트 계정 — 실서비스 전 삭제 필수
    try:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("admin", hash_password("admin1234"))
        )
        conn.commit()
        print("✅ 테스트 계정 생성 완료 (admin / admin1234)")
    except sqlite3.IntegrityError:
        print("ℹ️  테스트 계정이 이미 존재합니다.")
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
    print("\n새 계정 만들기 (그냥 Enter 누르면 건너뜀)")
    username = input("아이디: ").strip()
    if username:
        password = input("비밀번호: ").strip()
        signup(username, password)
