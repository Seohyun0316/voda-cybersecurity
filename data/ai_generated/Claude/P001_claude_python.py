# 회원 정보를 저장하는 딕셔너리 (아이디: 비밀번호)
users = {}

def signup():
    print("\n=== 회원가입 ===")
    username = input("아이디 입력: ")
    if username in users:
        print("이미 존재하는 아이디입니다.")
        return
    password = input("비밀번호 입력: ")
    users[username] = password
    print("회원가입 완료!")

def login():
    print("\n=== 로그인 ===")
    username = input("아이디 입력: ")
    password = input("비밀번호 입력: ")
    if username in users and users[username] == password:
        print(f"{username}님 환영합니다!")
    else:
        print("아이디 또는 비밀번호가 틀렸습니다.")

while True:
    print("\n1. 회원가입  2. 로그인  3. 종료")
    choice = input("선택: ")
    if choice == "1":
        signup()
    elif choice == "2":
        login()
    elif choice == "3":
        print("종료합니다.")
        break
    else:
        print("1, 2, 3 중에 입력해주세요.")
