import mysql.connector

# DB 연결
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mypass1234",
    database="userdb"
)

cursor = conn.cursor()

# 입력
id = input("아이디: ")
pw = input("비밀번호: ")

# DB 조회
sql = "SELECT * FROM users WHERE id = %s AND pw = %s"
cursor.execute(sql, (id, pw))

# 결과 확인
user = cursor.fetchone()

if user:
    print("로그인 성공!")
else:
    print("로그인 실패!")

cursor.close()
conn.close()