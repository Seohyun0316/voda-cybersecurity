import sqlite3

def check_id_exists(username):
    # 1. DB 연결 (예시로 memory DB 사용, 실제 파일 경로로 변경 가능)
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # 임시 테이블 생성 및 샘플 데이터 삽입 (테스트용)
    cursor.execute("CREATE TABLE users (id TEXT, pw TEXT)")
    cursor.execute("INSERT INTO users VALUES ('user123', 'password123')")

    # ================= [핵심 SQL 확인 부분] =================
    # ? 기능을 사용해 SQL 인젝션을 방지하는 것이 정석입니다.
    sql = "SELECT 1 FROM users WHERE id = ?"
    cursor.execute(sql, (username,))
    
    # 결과가 있으면 (1,) 튜플이 반환되고, 없으면 None이 반환됩니다.
    result = cursor.fetchone()
    # =======================================================

    conn.close()
    
    # result가 None이 아니면 True(존재함), None이면 False(없음)
    return result is not None

# 테스트
print(check_id_exists("user123"))  # True (존재함)
print(check_id_exists("unknown"))  # False (존재하지 않음)