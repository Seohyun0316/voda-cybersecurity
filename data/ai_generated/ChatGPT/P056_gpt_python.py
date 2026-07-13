name = input("이름을 입력하세요: ")

sql = "SELECT * FROM users WHERE name = %s"
cursor.execute(sql, (name,))

users = cursor.fetchall()

if users:
    for user in users:
        print(user)
else:
    print("검색 결과가 없습니다.")