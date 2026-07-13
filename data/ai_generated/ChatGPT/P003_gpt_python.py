import sqlite3

# DB 연결
conn = sqlite3.connect("user.db")
cur = conn.cursor()

# 테이블 생성
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    pw TEXT
)
""")

# 회원가입
id = input("아이디를 입력하세요: ")
pw = input("비밀번호를 입력하세요: ")

try:
    cur.execute("INSERT INTO users VALUES (?, ?)", (id, pw))
    conn.commit()
    print("회원가입이 완료되었습니다.")
except:
    print("이미 존재하는 아이디입니다.")

# DB 종료
conn.close()