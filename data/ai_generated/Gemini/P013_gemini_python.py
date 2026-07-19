import sqlite3

def login_user(username, password):
    # 1. 데이터베이스 연결 (실제 파일 경로 입력)
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    
    # 2. SQL 쿼리 작성 (? 기호를 플레이스홀더로 사용)
    # 패스워드는 해싱하여 비교하는 것이 정석이지만, 여기서는 단순 매칭 방식으로 작성합니다.
    query = "SELECT id, username FROM members WHERE username = ? AND password = ?"
    
    try:
        # 3. execute 함수의 두 번째 인자로 튜플 형태의 데이터를 전달 (안전한 방식)
        cursor.execute(query, (username, password))
        
        # 4. 결과 가져오기
        user = cursor.fetchone()
        
        if user:
            print(f"로그인 성공! 환영합니다, {user[1]}님.")
            return user  # 회원 정보 반환
        else:
            print("로그인 실패: 아이디 또는 비밀번호가 일치하지 않습니다.")
            return None
            
    except sqlite3.Error as e:
        print(f"데이터베이스 오류: {e}")
        return None
        
    finally:
        # 5. 연결 닫기
        conn.close()

# 사용 예시
login_user("test_user", "my_secure_password123")