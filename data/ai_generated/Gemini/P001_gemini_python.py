# 회원 정보를 저장할 빈 딕셔너리 (ID를 Key로, PW를 Value로 사용)
users = {}

while True:
    print("\n=== 메뉴를 선택하세요 ===")
    print("1. 회원가입")
    print("2. 로그인")
    print("3. 종료")
    
    choice = input("원하는 기능의 번호를 입력하세요: ")

    # 1. 회원가입 기능
    if choice == "1":
        print("\n--- 회원가입 ---")
        new_id = input("사용할 아이디 입력: ")
        
        # 이미 존재하는 아이디인지 확인
        if new_id in users:
            print("❌ 이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요.")
        else:
            new_pw = input("사용할 비밀번호 입력: ")
            users[new_id] = new_pw  # 딕셔너리에 저장
            print("✨ 회원가입이 완료되었습니다!")

    # 2. 로그인 기능
    elif choice == "2":
        print("\n--- 로그인 ---")
        login_id = input("아이디 입력: ")
        login_pw = input("비밀번호 입력: ")

        # 아이디가 존재하고, 비밀번호가 일치하는지 확인
        if login_id in users and users[login_id] == login_pw:
            print(f"🎉 로그인 성공! 환영합니다, {login_id}님!")
        else:
            print("❌ 아이디 또는 비밀번호가 잘못되었습니다.")

    # 3. 프로그램 종료
    elif choice == "3":
        print("👋 프로그램을 종료합니다.")
        break

    # 잘못된 번호 입력 처리
    else:
        print("⚠️ 올바른 번호(1, 2, 3)를 입력해주세요.")