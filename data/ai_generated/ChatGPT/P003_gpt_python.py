import sqlite3

# DB 연결
conn = sqlite3.connect("member.db")
cursor = conn.cursor()

# 회원 테이블 생성
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT
)
""")

# 회원가입 함수
def register():
    print("=== 회원가입 ===")

    username = input("아이디 입력: ")
    password = input("비밀번호 입력: ")
    email = input("이메일 입력: ")

    # 아이디 중복 확인
    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    )

    if cursor.fetchone():
        print("이미 존재하는 아이디입니다.")
        return

    # DB 저장
    cursor.execute(
        "INSERT INTO users(username, password, email) VALUES(?,?,?)",
        (username, password, email)
    )

    conn.commit()

    print("회원가입 완료!")


# 회원 목록 확인
def show_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    print("\n=== 회원 목록 ===")
    for user in users:
        print(user)


# 실행
register()
show_users()

conn.close()