import sqlite3

def search_products(user_input):
    # 데이터베이스 연결 (예시)
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    # ❌ 절대 하지 말아야 할 방식 (SQL Injection 취약)
    # query = f"SELECT * FROM products WHERE name LIKE '%{user_input}%'"
    # cursor.execute(query)
    
    #  안전한 방식: 플레이스홀더(?)를 사용하고 인자는 튜플로 전달
    query = "SELECT id, name, price FROM products WHERE name LIKE ?"
    
    # LIKE 절을 사용하기 위해 검색어 앞뒤로 %를 붙여줍니다.
    search_term = f"%{user_input}%"
    
    # execute 함수의 두 번째 인자로 바인딩할 데이터를 넘깁니다.
    cursor.execute(query, (search_term,))
    
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return results

# 사용 예시
# 사용자가 "노트북' OR '1'='1" 같은 악의적인 값을 넣어도 안전하게 문자로만 검색합니다.
search_results = search_products("아이폰")