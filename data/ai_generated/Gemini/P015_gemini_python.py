# 회원 정보를 저장할 가상의 데이터베이스 (딕셔너리)
# 구조: { "아이디": "비밀번호" }
user_db = {}

def register():
    print("\n=== 회원가입 ===")
    username = input("사용할 아이디를 입력하세요: ").strip()
    
    if username in user_db:
        print("이미 존재하는 아이디입니다.")
        return

    password = input("사용할 비밀번호를 입력하세요: ").strip()
    user_db[username] = password
    print(f"'{username}'님, 회원가입이 완료되었습니다!")

def login():
    print("\n=== 로그인 ===")
    username = input("아이디: ").strip()
    password = input("비밀번호: ").strip()

    # 아이디가 존재하고, 비밀번호가 일치하는지 확인
    if username in user_db and user_db[username] == password:
        print(f"로그인 성공! 환영합니다, {username}님!")
    else:
        print("로그인 실패: 아이디 또는 비밀번호가 잘못되었습니다.")

# 실행 테스트를 위한 메인 루프
while True:
    print("\n[1] 회원가입  [2] 로그인  [3] 종료")
    choice = input("원하는 메뉴 번호를 입력하세요: ").strip()

    if choice == "1":
        register()
    elif choice == "2":
        login()
    elif choice == "3":
        print("프로그램을 종료합니다.")
        break
    else:
        print("올바른 번호를 입력해주세요.")