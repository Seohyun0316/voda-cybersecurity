import sqlite3
import hashlib

# DB 연결
conn = sqlite3.connect("member.db")
cursor = conn.cursor()

# 회원 테이블 생성
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
""")


# 비밀번호 해싱 함수
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# 회원가입 함수
def register():
    username = input("아이디 입력: ")
    password = input("비밀번호 입력: ")

    # 비밀번호 암호화(해싱)
    hashed_password = hash_password(password)

    # DB 저장
    cursor.execute(
        "INSERT INTO users(username, password) VALUES (?, ?)",
        (username, hashed_password)
    )

    conn.commit()

    print("회원가입 완료!")


# 회원가입 실행
register()


# 저장된 데이터 확인
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

print("\nDB 저장 내용")
for user in users:
    print(user)


conn.close()        # False