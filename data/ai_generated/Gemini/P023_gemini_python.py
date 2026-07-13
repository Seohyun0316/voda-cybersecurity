import sqlite3
import bcrypt

# 1. 더미 데이터베이스 및 테이블 생성 (테스트용)
def init_db():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # 회원 테이블 생성 (비밀번호는 암호화되어 저장될 것이므로 TEXT 타입)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # 테스트용 학번 생성 (비밀번호 'password123!'를 암호화해서 저장)
    raw_password = "password123!"
    hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        cursor.execute(
            "INSERT INTO members (student_id, name, password) VALUES (?, ?, ?)",
            ('202612345', '김철수', hashed_password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # 이미 데이터가 있는 경우는 넘어갑니다.
        pass
        
    conn.close()

# 2. 로그인 검증 함수
def login_library(student_id, input_password):
    # DB 연결
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    
    # [보안 조치] SQL 인젝션을 방지하기 위해 쿼리에 바로 문자열을 더하지 않고 ? (Placeholder)를 사용합니다.
    # 학번이 일치하는 사용자의 암호화된 비밀번호와 이름을 가져옵니다.
    query = "SELECT name, password FROM members WHERE student_id = ?"
    cursor.execute(query, (student_id,))
    
    result = cursor.fetchone()
    conn.close()
    
    # 해당 학번의 학생이 존재하지 않는 경우
    if not result:
        return False, "존재하지 않는 학번입니다."
    
    db_name, hashed_password = result
    
    # 입력받은 비밀번호와 DB에 저장된 암호화된 비밀번호를 비교
    # bcrypt.checkpw는 알아서 솔팅(Salt)을 감안하여 두 비밀번호가 일치하는지 검증합니다.
    if bcrypt.checkpw(input_password.encode('utf-8'), hashed_password.encode('utf-8')):
        return True, f"{db_name}님, 환영합니다! 로그인에 성공했습니다."
    else:
        return False, "비밀번호가 일치하지 않습니다."

# --- 실행 및 테스트 ---
if __name__ == "__main__":
    # 데이터베이스 초기화 (최초 1회 실행)
    init_db()
    
    print("--- 도서관 좌석 예약 시스템 로그인 ---")
    input_id = input("학번을 입력하세요: ")
    input_pw = input("비밀번호를 입력하세요: ")
    
    # 로그인 시도
    success, message = login_library(input_id, input_pw)
    
    print("\n[결과]")
    print(message)