def run_event_program():
    # 응모자 정보를 저장할 리스트 (딕셔너리 형태로 저장)
    applicants = []

    print("====================================")
    print("🎉 이벤트 응모 프로그램이 시작되었습니다! 🎉")
    print("====================================")

    while True:
        print("\n[메뉴를 선택하세요]")
        print("1. 이벤트 응모하기")
        print("2. 응모자 목록 보기")
        print("3. 프로그램 종료")
        
        choice = input("👉 선택 (1/2/3): ").strip()

        if choice == '1':
            print("\n--- [응모 정보 입력] ---")
            name = input("👤 이름: ").strip()
            phone = input("📞 전화번호: ").strip()

            # 간단한 유효성 검사 (입력값이 비어있는지 확인)
            if not name or not phone:
                print("⚠️ 이름과 전화번호는 필수 입력 항목입니다. 다시 시도해주세요.")
                continue

            # 응모자 정보 저장
            applicant = {"이름": name, "전화번호": phone}
            applicants.append(applicant)
            print(f"✨ {name}님의 응모가 성공적으로 완료되었습니다!")

        elif choice == '2':
            print("\n--- [📋 현재 응모자 목록] ---")
            if not applicants:
                print("아직 응모자가 없습니다. 첫 번째 응모자가 되어보세요!")
            else:
                print(f"총 {len(applicants)}명 응모 중\n")
                print(f"{'번호':<5} | {'이름':<10} | {'전화번호':<15}")
                print("-" * 35)
                for index, app in enumerate(applicants, start=1):
                    print(f"{index:<5} | {app['이름']:<10} | {app['전화번호']:<15}")
            print("-" * 35)

        elif choice == '3':
            print("\n👋 프로그램을 종료합니다. 이용해 주셔서 감사합니다!")
            break
        else:
            print("❌ 잘못된 선택입니다. 1, 2, 3 중에서 다시 골라주세요.")

# 프로그램 실행
if __name__ == "__main__":
    run_event_program()