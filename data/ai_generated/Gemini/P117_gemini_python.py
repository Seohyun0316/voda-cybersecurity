import sqlite3
from datetime import datetime

def print_birthday_customers():
    # 1. DB 연결 (본인의 DB 파일 경로로 변경하세요)
    conn = sqlite3.connect('customers.db')
    cursor = conn.cursor()
    
    # 2. 오늘 날짜 구하기 (MM-DD 형식)
    today = datetime.now().strftime('%m-%d')
    print(f"=== [ {datetime.now().strftime('%Y-%m-%d')} ] 오늘 생일자 조회 결과 ===")
    
    # 3. SQL 쿼리 작성 (생일 컬럼이 'YYYY-MM-DD' 형식이라고 가정)
    # strftime('%m-%d', birthday)를 통해 월과 일만 비교합니다.
    query = """
        SELECT id, name, phone, birthday 
        FROM customers 
        WHERE strftime('%m-%d', birthday) = ?
    """
    
    try:
        cursor.execute(query, (today,))
        rows = cursor.fetchall()
        
        if not rows:
            print("오늘 생일인 고객이 없습니다.")
            return
            
        # 4. 결과 출력
        for row in rows:
            customer_id, name, phone, birthday = row
            print(f"ID: {customer_id} | 이름: {name} | 연락처: {phone} | 생일: {birthday}")
            
    except sqlite3.Error as e:
        print(f"데이터베이스 에러 발생: {e}")
        
    finally:
        # 5. 연결 종료
        conn.close()

# 코드 실행
if __name__ == "__main__":
    print_birthday_customers()