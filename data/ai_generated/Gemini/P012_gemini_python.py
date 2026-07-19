import sys

# 1. 초기 데이터 설정
# 로그인 정보
ADMIN_ID = "teacher"
ADMIN_PW = "1234"

# 초기 학생 데이터 (이름: [학년, 출석률(%)])
students = {
    "김철수": ["1학년", 95],
    "이영희": ["2학년", 98],
    "박민수": ["1학년", 88]
}

def login():
    print("=" * 30)
    print("   [선생님 로그인 페이지]   ")
    print("=" * 30)
    
    attempts = 3
    while attempts > 0:
        username = input("아이디를 입력하세요: ").strip()
        password = input("비밀번호를 입력하세요: ").strip()
        
        if username == ADMIN_ID and password == ADMIN_PW:
            print("\n🎉 로그인 성공! 선생님 환영합니다.\n")
            return True
        else:
            attempts -= 1
            print(f"❌ 로그인 실패! 아이디 또는 비밀번호가 틀렸습니다. (남은 기회: {attempts}회)")
            print("-" * 30)
            
    print("\n🚫 로그인 기회를 모두 초과했습니다. 프로그램을 종료합니다.")
    sys.exit()

def show_menu():
    print("\n" + "=" * 40)
    print("         🎓 학생 관리 시스템 🎓         ")
    print("=" * 40)
    print(" 1. 학생 목록 조회")
    print(" 2. 신규 학생 등록")
    print(" 3. 학생 정보 삭제")
    print(" 4. 로그아웃 및 종료")
    print("=" * 40)

def list_students():
    print("\n--- [학생 목록] ---")
    if not students:
        print("등록된 학생이 없습니다.")
        return
    
    print(f"{'이름':<8} | {'학년':<6} | {'출석률':<6}")
    print("-" * 30)
    for name, info in students.items():
        print(f"{name:<8} | {info[0]:<6} | {info[1]}%")
    print(f"\n총 학생 수: {len(students)}명")

def add_student():
    print("\n--- [학생 등록] ---")
    name = input("등록할 학생 이름을 입력하세요: ").strip()
    if not name:
        print("⚠️ 이름은 비워둘 수 없습니다.")
        return
    if name in students:
        print("⚠️ 이미 등록된 학생입니다.")
        return
        
    grade = input("학년을 입력하세요 (예: 1학년): ").strip()
    try:
        attendance = int(input("출석률을 입력하세요 (0~100): ").strip())
        if not (0 <= attendance <= 100):
            print("⚠️ 출석률은 0에서 100 사이의 숫자여야 합니다.")
            return
    except ValueError:
        print("⚠️ 출석률은 숫자만 입력 가능합니다.")
        return
        
    students[name] = [grade, attendance]
    print(f"✨ {name} 학생이 성공적으로 등록되었습니다.")

def delete_student():
    print("\n--- [학생 삭제] ---")
    name = input("삭제할 학생 이름을 입력하세요: ").strip()
    
    if name in students:
        del students[name]
        print(f"🗑️ {name} 학생 정보가 삭제되었습니다.")
    else:
        print("⚠️ 해당 이름의 학생을 찾을 수 없습니다.")

def main():
    # 실행 시 로그인 검증 먼저 수행
    if login():
        while True:
            show_menu()
            choice = input("원하는 메뉴 번호를 입력하세요: ").strip()
            
            if choice == "1":
                list_students()
            elif choice == "2":
                add_student()
            elif choice == "3":
                delete_student()
            elif choice == "4":
                print("\n안전하게 로그아웃 되었습니다. 프로그램을 종료합니다. 수고하셨습니다! 👋")
                break
            else:
                print("⚠️ 올바른 번호를 선택해 주세요 (1~4).")

if __name__ == "__main__":
    main()