def register_student():
    student_id = input("학번: ")
    name = input("이름: ")
    address = input("주소: ")
    guardian_phone = input("보호자 연락처: ")

    # 디버깅 출력
    print("\n===== 입력 데이터 확인 =====")
    print("학번:", student_id)
    print("이름:", name)
    print("주소:", address)
    print("보호자 연락처:", guardian_phone)
    print("===========================")


register_student()