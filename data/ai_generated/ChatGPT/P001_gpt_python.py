# 회원 정보 저장
users = {}

while True:
    print("\n===== 메뉴 =====")
    print("1. 회원가입")
    print("2. 로그인")
    print("3. 종료")

    menu = input("번호를 선택하세요: ")

    if menu == "1":
        # 회원가입
        id = input("아이디: ")

        if id in users:
            print("이미 있는 아이디입니다.")
        else:
            pw = input("비밀번호: ")
            users[id] = pw
            print("회원가입이 완료되었습니다.")

    elif menu == "2":
        # 로그인
        id = input("아이디: ")
        pw = input("비밀번호: ")

        if id in users and users[id] == pw:
            print("로그인 성공!")
        else:
            print("아이디 또는 비밀번호가 틀렸습니다.")

    elif menu == "3":
        print("프로그램을 종료합니다.")
        break

    else:
        print("잘못 입력했습니다.")