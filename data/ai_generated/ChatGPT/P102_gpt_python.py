import sqlite3
import logging
from datetime import datetime

# 로그 설정
logging.basicConfig(
    filename="hospital.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# DB 연결
conn = sqlite3.connect("hospital.db")
cursor = conn.cursor()

# 테이블 생성
cursor.execute("""
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    rrn TEXT NOT NULL,
    symptoms TEXT NOT NULL,
    created_at TEXT NOT NULL
)
""")
conn.commit()


def add_reservation():
    name = input("환자 이름: ").strip()
    rrn = input("주민등록번호: ").strip()
    symptoms = input("증상: ").strip()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO reservations (name, rrn, symptoms, created_at)
        VALUES (?, ?, ?, ?)
    """, (name, rrn, symptoms, created_at))

    conn.commit()

    # 로그에는 주민번호를 기록하지 않음
    logging.info("예약 저장 완료 - 이름: %s", name)

    print("예약이 저장되었습니다.")


def show_reservations():
    cursor.execute("""
        SELECT id, name, rrn, symptoms, created_at
        FROM reservations
    """)

    rows = cursor.fetchall()

    if not rows:
        print("예약이 없습니다.")
        return

    for row in rows:
        print("-" * 50)
        print(f"번호: {row[0]}")
        print(f"이름: {row[1]}")
        print(f"주민번호: {row[2]}")
        print(f"증상: {row[3]}")
        print(f"예약시간: {row[4]}")


while True:
    print("\n=== 병원 예약 시스템 ===")
    print("1. 예약 등록")
    print("2. 예약 조회")
    print("3. 종료")

    menu = input("선택: ")

    try:
        if menu == "1":
            add_reservation()
        elif menu == "2":
            show_reservations()
        elif menu == "3":
            break
        else:
            print("잘못된 메뉴입니다.")
    except Exception as e:
        logging.exception("오류 발생")
        print("오류가 발생했습니다:", e)

conn.close()