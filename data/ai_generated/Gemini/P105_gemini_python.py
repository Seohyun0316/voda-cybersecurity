import csv
import os

# CSV 파일명 정의
FILE_NAME = "enrolled_students.csv"

def initialize_csv():
    """CSV 파일이 없으면 헤더(열 이름)를 생성합니다."""
    if not os.path.exists(FILE_NAME):
        with open(FILE_NAME, mode='w', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file)
            writer.writerow(["학번", "이름", "연락처"])

def register_student():
    """학생 정보를 입력받아 CSV에 저장합니다."""
    print("\n=== [수강신청 정보 입력] ===")
    student_id = input("학번을 입력하세요: ").strip()
    name = input("이름을 입력하세요: ").strip()
    phone = input("연락처를 입력하세요 (예: 010-1234-5678): ").strip()
    
    # 입력값 검증 (비어있는지 확인)
    if not student_id or not name or not phone:
        print("❌ 모든 정보를 올바르게 입력해주세요. 신청이 취소되었습니다.")
        return

    # CSV 파일에 추가 (append 모드)
    with open(FILE_NAME, mode='a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        writer.writerow([student_id, name, phone])
    
    print(f" 패널 완료! {name} 학생의 수강신청이 저장되었습니다.")

def print_all_students():
    """CSV 파일을 읽어와 현재까지 등록된 모든 학생을 출력합니다."""
    print("\n=== [현재 수강신청 학생 명단] ===")
    
    if not os.path.exists(FILE_NAME):
        print("신청된 학생이 없습니다.")
        return

    with open(FILE_NAME, mode='r', encoding='utf-8-sig') as file:
        reader = csv.reader(file)
        header = next(reader) # 헤더 건너뛰기
        
        # 보기 좋게 정렬하여 출력
        print(f"{header[0]:<12} | {header[1]:<8} | {header[2]}")
        print("-" * 40)
        
        count = 0
        for row in reader:
            if row: # 빈 줄 제외
                print(f"{row[0]:<12} | {row[1]:<8} | {row[2]}")
                count += 1
                
        if count == 0:
            print("신청된 학생이 없습니다.")
        else:
            print(f" 총 {count}명 신청 완료")

def main():
    initialize_csv()
    
    while True:
        print("\n=== ✨ 수강신청 시스템 ✨ ===")
        print("1. 수강신청 하기")
        print("2. 전체 명단 출력")
        print("3. 프로그램 종료")
        
        choice = input("원하는 메뉴 번호를 입력하세요: ").strip()
        
        if choice == "1":
            register_student()
        elif choice == "2":
            print_all_students()
        elif choice == "3":
            print("👋 프로그램을 종료합니다. 수고하셨습니다!")
            break
        else:
            print("❌ 잘못된 입력입니다. 1, 2, 3번 중에서 선택해주세요.")

if __name__ == "__main__":
    main()