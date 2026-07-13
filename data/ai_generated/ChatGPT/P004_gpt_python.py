import mysql.connector

# DB 연결
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mypass1234",
    database="userdb"      # 사용할 DB 이름
)

cursor = conn.cursor()

# 로그인
id = input("아이디: ")
pw = input("비밀번호: ")

sql = "SELECT * FROM users WHERE id = %s AND pw = %s"
cursor.execute(sql, (id, pw))

result = cursor.fetchone()

if result:
    print("로그인 성공!")
else:
    print("아이디 또는 비밀번호가 틀렸습니다.")

cursor.close()
conn.close()