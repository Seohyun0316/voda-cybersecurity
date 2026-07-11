import sqlite3

# 1. 데이터베이스 파일 연결 (파일이 없으면 자동으로 생성됩니다)
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# 2. 회원 정보를 저장할 테이블(장부) 만들기 (처음 한 번만 실행됨)
# id는 중복을 방지하기 위해 PRIMARY KEY(기본키)로 설정합니다.
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    pw TEXT
)
""")
conn.commit()


while True:
    print("\n=== [DB 연동] 메뉴를 선택하세요 ===")
    print("1. 회원가입")
    print("2. 로그인")
    print("3. 종료")
    
    choice = input("원하는 기능의 번호를 입력하세요: ")

    # [회원가입 기능]
    if choice == "1":
        print("\n--- 회원가입 ---")
        new_id = input("사용할 아이디 입력: ")
        
        # DB에서 해당 아이디가 이미 존재하는지 조회
        cursor.execute("SELECT id FROM users WHERE id = ?", (new_id,))
        row = cursor.fetchone()
        
        if row:
            print("❌ 이미 존재하는 아이디입니다. 다른 아이디를 사용해주세요.")
        else:
            new_pw = input("사용할 비밀번호 입력: ")
            # DB에 새로운 회원 정보 삽입 (INSERT)
            cursor.execute("INSERT INTO users (id, pw) VALUES (?, ?)", (new_id, new_pw))
            conn.commit() # 데이터 변경사항을 실제로 DB 파일에 저장
            print("✨ 회원가입이 완료되었습니다! (DB 저장 완료)")

    # [로그인 기능]
    elif choice == "2":
        print("\n--- 로그인 ---")
        login_id = input("아이디 입력: ")
        login_pw = input("비밀번호 입력: ")

        # 입력한 아이디와 비밀번호가 일치하는 데이터가 있는지 조회
        cursor.execute("SELECT id FROM users WHERE id = ? AND pw = ?", (login_id, login_pw))
        row = cursor.fetchone()

        if row:
            print(f"🎉 로그인 성공! 환영합니다, {login_id}님!")
        else:
            print("❌ 아이디 또는 비밀번호가 잘못되었습니다.")

    # [프로그램 종료]
    elif choice == "3":
        print("👋 프로그램을 종료합니다.")
        break
        
    else:
        print("⚠️ 올바른 번호(1, 2, 3)를 입력해주세요.")

# 3. 프로그램이 완전히 끝나기 전 DB 연결 닫기
conn.close()