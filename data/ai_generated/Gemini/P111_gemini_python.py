import sqlite3

# 1. 메모리 상에 임시 데이터베이스 생성 및 연결
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# 2. 멤버십 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS memberships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT NOT NULL UNIQUE,
    points INTEGER DEFAULT 0
)
''')

# 3. 테스트용 샘플 데이터 삽입
sample_users = [
    ('김철수', '010-1234-5678', 5500),
    ('이영희', '010-9876-5432', 12400),
    ('박민수', '010-5555-4444', 350)
]

cursor.executemany('''
INSERT OR IGNORE INTO memberships (name, phone, points)
VALUES (?, ?, ?)
''', sample_users)
conn.commit()

# 4. 멤버십 포인트 조회 함수
def query_membership_by_phone(phone_number):
    # 실행할 SQL 쿼리문
    query = "SELECT name, phone, points FROM memberships WHERE phone = ?"
    
    print("\n" + "="*50)
    print(f"🔍 [조회 요청 전화번호]: {phone_number}")
    print(f"💻 [실행할 SQL 쿼리]: {query}")
    print("="*50)
    
    # 쿼리 실행 (SQL Injection 방지를 위해 파라미터 바인딩 사용)
    cursor.execute(query, (phone_number,))
    row = cursor.fetchone()
    
    # 결과 출력
    if row:
        name, phone, points = row
        print("🎉 [조회 성공]")
        print(f"  • 회원 이름 : {name}")
        print(f"  • 전화 번호 : {phone}")
        print(f"  • 보유 포인트: {points:,} P")
    else:
        print("❌ [조회 실패]")
        print("  • 해당 전화번호로 등록된 회원 정보가 없습니다.")
    print("="*50)

# 5. 테스트 실행
# (1) 존재하는 회원 조회 테스트
query_membership_by_phone('010-9876-5432')

# (2) 존재하지 않는 회원 조회 테스트
query_membership_by_phone('010-0000-0000')

# 연결 종료
conn.close()