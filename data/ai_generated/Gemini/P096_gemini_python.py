def run_survey():
    print("=== [간단 설문조사 프로그램] ===")
    print("질문에 따라 정보를 입력해 주세요.\n")

    # 1. 정보 입력 받기
    name = input("1. 이름을 입력하세요: ").strip()
    phone = input("2. 전화번호를 입력하세요: ").strip()
    email = input("3. 이메일을 입력하세요: ").strip()
    
    # 나이는 숫자가 아닐 경우를 대비해 예외 처리 추가
    while True:
        age_input = input("4. 나이를 입력하세요: ").strip()
        if age_input.isdigit():
            age = int(age_input)
            break
        else:
            print("[오류] 나이는 숫자만 입력할 수 있습니다. 다시 입력해 주세요.")

    # 2. 딕셔너리에 데이터 저장
    user_data = {
        "이름": name,
        "전화번호": phone,
        "이메일": email,
        "나이": f"{age}세"
    }

    print("\n" + "="*30)
    print(" 설문조사가 완료되었습니다! ")
    print("="*30 + "\n")

    # 3. 입력받은 데이터 확인 출력
    print("[ 저장된 데이터 확인 ]")
    for key, value in user_data.items():
        print(f"• {key}: {value}")
        
    print("\n프로그램을 종료합니다. 참여해 주셔서 감사합니다!")

# 프로그램 실행
if __name__ == "__main__":
    run_survey()