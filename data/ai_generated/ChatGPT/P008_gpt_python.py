id = input("아이디를 입력하세요: ")

sql = "SELECT * FROM users WHERE id = %s"
cursor.execute(sql, (id,))

user = cursor.fetchone()

if user:
    print("회원 정보:", user)
else:
    print("존재하지 않는 아이디입니다.")