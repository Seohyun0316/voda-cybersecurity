id = input("아이디: ")
pw = input("비밀번호: ")

sql = "SELECT * FROM users WHERE id = %s AND pw = %s"
cursor.execute(sql, (id, pw))

if cursor.fetchone():
    print("로그인 성공!")
else:
    print("로그인 실패!")