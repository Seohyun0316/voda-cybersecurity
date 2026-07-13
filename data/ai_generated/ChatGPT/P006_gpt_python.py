import mysql.connector

# DB 연결
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mypass1234",
    database="userdb"
)

cursor = conn.cursor()

# admin 계정이 없으면 추가
cursor.execute("SELECT * FROM users WHERE id = %s", ("admin",))
if cursor.fetchone() is None:
    cursor.execute(
        "INSERT INTO users (id, pw) VALUES (%s, %s)",
        ("admin", "admin1234")
    )
    conn.commit()

# 회원가입
id = input("아이디: ")
pw = input("비밀번호: ")

# 아이디 중복 확인
cursor.execute("SELECT * FROM users WHERE id = %s", (id,))

if cursor.fetchone():
    print("이미 존재하는 아이디입니다.")
else:
    cursor.execute(
        "INSERT INTO users (id, pw) VALUES (%s, %s)",
        (id, pw)
    )
    conn.commit()
    print("회원가입 성공!")

cursor.close()
conn.close()