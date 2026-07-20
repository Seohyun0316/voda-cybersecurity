import csv
from datetime import datetime
import os


FILE_NAME = "waiting_list.csv"


def save_waiting_person():
    print("=== 상담 대기자 등록 ===")

    name = input("이름: ")
    phone = input("연락처: ")

    data = {
        "name": name,
        "phone": phone,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


    # 파일이 없으면 헤더 생성
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
                "name",
                "phone",
                "created_at"
            ]
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(data)


    print("\n등록 완료")
    print(data)



def show_waiting_list():
    print("\n=== 상담 대기자 목록 ===")

    if not os.path.exists(FILE_NAME):
        print("등록된 대기자가 없습니다.")
        return

    with open(
        FILE_NAME,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for index, row in enumerate(reader, start=1):
            print(
                f"{index}. "
                f"{row['name']} / "
                f"{row['phone']} / "
                f"{row['created_at']}"
            )



if __name__ == "__main__":

    while True:
        print("""
1. 상담 대기 등록
2. 대기자 조회
3. 종료
""")

        menu = input("선택: ")

        if menu == "1":
            save_waiting_person()

        elif menu == "2":
            show_waiting_list()

        elif menu == "3":
            print("종료")
            break

        else:
            print("잘못된 선택입니다.")