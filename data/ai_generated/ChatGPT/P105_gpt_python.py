import csv
import os

CSV_FILE = "students.csv"

def register_student():
    student_id = input("학번: ")
    name = input("이름: ")
    phone = input("연락처: ")

    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["학번", "이름", "연락처"])

        writer.writerow([student_id, name, phone])

    print("수강신청이 저장되었습니다.")

def print_all_students():
    if not os.path.exists(CSV_FILE):
        print("저장된 신청 내역이 없습니다.")
        return

    print("\n=== 수강신청 목록 ===")

    with open(CSV_FILE, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for row in reader:
            print(row)

while True:
    print("\n=== 수강신청 프로그램 ===")
    print("1. 신청")
    print("2. 전체 출력")
    print("3. 종료")

    choice = input("선택: ")

    if choice == "1":
        register_student()
    elif choice == "2":
        print_all_students()
    elif choice == "3":
        break
    else:
        print("잘못된 메뉴입니다.")