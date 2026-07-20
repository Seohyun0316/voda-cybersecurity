users = {}

def register():
    username = input("아이디: ")
    password = input("비밀번호: ")
    users[username] = password
    print("회원가입 완료!")

def login():
    username = input("아이디: ")
    password = input("비밀번호: ")
    if users.get(username) == password:
        print(f"{username}님 로그인 성공!")
        return True
    print("아이디 또는 비밀번호가 틀렸습니다.")
    return False

if __name__ == '__main__':
    while True:
        print("\n1.회원가입 2.로그인 3.종료")
        choice = input("선택: ")
        if choice == '1':
            register()
        elif choice == '2':
            login()
        elif choice == '3':
            break
