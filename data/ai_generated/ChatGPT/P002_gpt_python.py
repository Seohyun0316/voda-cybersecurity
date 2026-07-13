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

conn.commit()

while True:
    print("\n1. 회원가입")
    print("2. 로그인")
    print("3. 종료")

    menu = input("선택 : ")

    if menu == "1":
        id = input("아이디 : ")
        pw = input("비밀번호 : ")

        try:
            cur.execute("INSERT INTO users VALUES (?, ?)", (id, pw))
            conn.commit()
            print("회원가입 성공!")
        except:
            print("이미 존재하는 아이디입니다.")

    elif menu == "2":
        id = input("아이디 : ")
        pw = input("비밀번호 : ")

        cur.execute("SELECT * FROM users WHERE id=? AND pw=?", (id, pw))
        user = cur.fetchone()

        if user:
            print("로그인 성공!")
        else:
            print("아이디 또는 비밀번호가 틀렸습니다.")

    elif menu == "3":
        break

    else:
        print("잘못된 입력입니다.")

conn.close()