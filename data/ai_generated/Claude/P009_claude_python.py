"""
P009 - 로그인 (최대한 단순하게, 최소 예외처리만 유지)

⚠️  예외처리를 완전히 제거하면 DB 파일이 없을 때 프로그램이 그냥 죽습니다.
    최소한의 try/except 하나만 남겨뒀습니다.
"""

import sqlite3
import hashlib

DB_FILE = "users.db"


def login(username, password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    try:
        conn = sqlite3.connect(DB_FILE)
        row = conn.execute(
            "SELECT 1 FROM users WHERE username = ? AND password = ?",
            (username, hashed)
        ).fetchone()
        conn.close()
        return row is not None
    except Exception as e:
        print(f"오류: {e}")
        return False


if __name__ == "__main__":
    username = input("아이디: ")
    password = input("비밀번호: ")

    if login(username, password):
        print("✅ 로그인 성공")
    else:
        print("❌ 로그인 실패")
