"""
P005 - SQL로 아이디 존재 확인 (SQLite, 최대한 간단하게)

⚠️  SQL을 문자열로 직접 조합하면 SQL 인젝션 공격에 취약합니다.
    반드시 ? 플레이스홀더를 사용하세요 (아래 코드가 안전한 방식입니다).
"""

import sqlite3

DB_FILE = "users.db"


def is_username_exists(username):
    """아이디가 DB에 있으면 True, 없으면 False"""
    conn = sqlite3.connect(DB_FILE)
    row = conn.execute(
        "SELECT 1 FROM users WHERE username = ?", (username,)  # ? 사용 → 안전
    ).fetchone()
    conn.close()
    return row is not None


if __name__ == "__main__":
    username = input("확인할 아이디: ")

    if is_username_exists(username):
        print(f"'{username}' 은(는) DB에 존재합니다.")
    else:
        print(f"'{username}' 은(는) DB에 없습니다.")
