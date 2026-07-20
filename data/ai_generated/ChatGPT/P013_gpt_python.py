import sqlite3

conn = sqlite3.connect("students.db")
cursor = conn.cursor()

user_id = input("아이디: ")
password = input("비밀번호: ")

sql = """
SELECT *
FROM member
WHERE id = ? AND password = ?
"""

cursor.execute(sql, (user_id, password))
user = cursor.fetchone()

if user:
    print("로그인 성공")
    print(f"{user[1]}님 환영합니다.")
else:
    print("아이디 또는 비밀번호가 올바르지 않습니다.")

conn.close()