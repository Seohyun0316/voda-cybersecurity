import sqlite3

def get_user_info(input_id):
    # 1. 데이터베이스 연결 (파일이 없으면 자동으로 생성됨)
    conn = sqlite3.connect('members.db')
    cursor = conn.cursor()
    
    try:
        # 임시 테이블 및 테스트 데이터 생성 (실제 DB가 있다면 이 부분은 제외)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT
            )
        ''')
        cursor.execute("INSERT OR IGNORE INTO users VALUES ('user123', '홍길동', 'hong@example.com')")
        conn.commit()

        # 2. SQL 쿼리 작성 및 실행
        # ⚠️ 중요: SQL 인젝션 방지를 위해 %s 나 f-string 대신 '?' 파라미터 바인딩을 사용합니다.
        query = "SELECT * FROM users WHERE user_id = ?"
        
        # execute의 두 번째 인자는 반드시 튜플(tuple) 형태여야 하므로 (input_id,) 로 전달합니다.
        cursor.execute(query, (input_id,))
        
        # 3. 결과 가져오기 (단건 조회의 경우 fetchone 사용)
        user_data = cursor.fetchone()
        
        if user_data:
            return {
                "user_id": user_data[0],
                "name": user_data[1],
                "email": user_data[2]
            }
        else:
            return None

    except sqlite3.Error as e:
        print(# 4. 연결 종료
f"데이터베이스 에러 발생: {e}")
        return None
        
    finally:
        cursor.close()
        conn.close()

# --- 실행 테스트 ---
search_id = "user123"
result = get_user_info(search_id)

if result:
    print(f"🎉 회원 정보를 찾았습니다!\n{result}")
else:
    print("❌ 일치하는 회원 정보가 없습니다.")