"""
P008 - 아이디로 회원 정보 DB에서 조회 (SQL 쿼리)

⚠️  SQL 인젝션 경고
    위험한 방식 (절대 사용 금지):
        query = "SELECT * FROM users WHERE username = '" + username + "'"
        → 해커가 username에 ' OR '1'='1 같은 값을 넣으면 DB 전체가 노출됩니다.

    안전한 방식 (아래 코드): ? 플레이스홀더 사용
"""

import sqlite3

DB_FILE = "users.db"


def find_user(username):
    """아이디로 사용자 정보 조회. 없으면 None 반환."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리처럼 사용 가능

    # ✅ 안전한 쿼리: ? 에 값을 따로 전달
    row = conn.execute(
        "SELECT id, username FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


if __name__ == "__main__":
    username = input("조회할 아이디: ")
    user = find_user(username)

    if user:
        print(f"찾은 사용자 → {user}")
    else:
        print("해당 아이디의 사용자가 없습니다.")
