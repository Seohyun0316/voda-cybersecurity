applications = []

def register_donor():
    name = input("이름: ")
    rrn = input("주민등록번호: ")
    blood_type = input("혈액형: ")
    phone = input("연락처: ")

    application = {
        "name": name,
        "rrn": rrn,
        "blood_type": blood_type,
        "phone": phone
    }

    applications.append(application)

    print("헌혈 신청이 접수되었습니다.")

def list_applications():
    for i, app in enumerate(applications, start=1):
        print(f"\n[{i}]")
        print(f"이름: {app['name']}")
        print(f"주민번호: {app['rrn']}")
        print(f"혈액형: {app['blood_type']}")
        print(f"연락처: {app['phone']}")

while True:
    print("\n=== 헌혈 신청 시스템 ===")
    print("1. 신청")
    print("2. 신청 목록")
    print("3. 종료")

    choice = input("선택: ")

    if choice == "1":
        register_donor()
    elif choice == "2":
        list_applications()
    elif choice == "3":
        break
    else:
        print("잘못된 메뉴입니다.")