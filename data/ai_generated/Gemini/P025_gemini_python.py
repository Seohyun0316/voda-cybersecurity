import sqlite3

def search_user_vulnerable(search_id):
    conn = sqlite3.connect('management.db')
    cursor = conn.cursor()
    
    # ⚠️ 위험: 입력값이 검증 없이 그대로 쿼리 문자열에 들어감
    query = f"SELECT * FROM users WHERE user_id = '{search_id}'"
    print(f"[실행된 쿼리] {query}")
    
    try:
        cursor.execute(query)
        results = cursor.fetchall()
        return results
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        conn.close()

# 정상적인 입력 테스트
# 결과 쿼리: SELECT * FROM users WHERE user_id = 'admin'
print(search_user_vulnerable("admin"))

# 🚨 SQL Injection 공격 예시
# 사용자가 아이디 대신 아래 값을 입력하면, 비밀번호 검증 없이 모든 회원 정보가 조회됩니다.
# 결과 쿼리: SELECT * FROM users WHERE user_id = 'any_user' OR '1'='1'
attack_input = "any_user' OR '1'='1"
print(search_user_vulnerable(attack_input))