import csv
import os
from datetime import datetime


FILE_NAME = "dormitory_application.csv"


def save_application():
    print("=== 기숙사 신청 ===")

    student_id = input("학번: ")
    name = input("이름: ")
    address = input("주소: ")
    guardian_phone = input("보호자 연락처: ")

    application = {
        "student_id": student_id,
        "name": name,
        "address": address,
        "guardian_phone": guardian_phone,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    file_exists = os.path.exists(FILE_NAME)

    with open(
        FILE_NAME,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "student_id",
                "name",
                "address",
                "guardian_phone",
                "created_at"
            ]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(application)


    print("\n===== 저장 완료 =====")
    print(application)



def show_applications():
    print("\n===== 기숙사 신청 목록 =====")

    if not os.path.exists(FILE_NAME):
        print("신청 데이터 없음")
        return

    with open(
        FILE_NAME,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for index, row in enumerate(reader, start=1):
            print(f"\n[{index}]")
            print(f"학번           : {row['student_id']}")
            print(f"이름           : {row['name']}")
            print(f"주소           : {row['address']}")
            print(f"보호자 연락처  : {row['guardian_phone']}")
            print(f"신청 시간      : {row['created_at']}")



if __name__ == "__main__":

    while True:
        print("""
====================
1. 기숙사 신청
2. 신청자 확인
3. 종료
====================
""")

        menu = input("선택: ")

        if menu == "1":
            save_application()

        elif menu == "2":
            show_applications()

        elif menu == "3":
            print("프로그램 종료")
            break

        else:
            print("잘못된 입력입니다.")