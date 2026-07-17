import sqlite3

def get_reviews_unsafe(user_input_rating):
    # 데이터베이스 연결 (예시용 메모리 DB)
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # 예시 테이블 및 데이터 생성
    cursor.execute("CREATE TABLE reviews (id INTEGER, content TEXT, rating TEXT)")
    cursor.execute("INSERT INTO reviews VALUES (1, '최고예요!', '5')")
    cursor.execute("INSERT INTO reviews VALUES (2, '그냥 그래요.', '3')")
    conn.commit()

    # ⚠️ 극도로 위험: 사용자의 입력값을 SQL 쿼리에 그대로 이어 붙임
    # 만약 user_input_rating에 "5' OR '1'='1" 이 들어오면 모든 데이터가 조회됨
    query = f"SELECT * FROM reviews WHERE rating = '{user_input_rating}'"
    print(f"[실행할 쿼리]: {query}")
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"에러 발생: {e}")
    finally:
        conn.close()

# --- 실행 테스트 ---
# 1. 정상적인 입력
print("정상 조회:", get_reviews_unsafe("5"))

# 2. SQL 인젝션 공격 입력 (별점이 3인 데이터까지 전부 조회됨)
print("공격 시나리오:", get_reviews_unsafe("5' OR '1'='1"))