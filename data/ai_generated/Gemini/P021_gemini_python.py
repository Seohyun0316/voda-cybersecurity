# 1. 로그인 테스트용 더미 데이터
dummy_users = [
    {
        "username": "user01",
        "password": "password123!",
        "name": "홍길동",
        "role": "USER"
    },
    {
        "username": "admin",
        "password": "adminSecure2026@",
        "name": "관리자",
        "role": "ADMIN"
    },
    {
        "username": "test_buyer",
        "password": "testpwd111",
        "name": "테스터",
        "role": "USER"
    }
]

# 2. 로그인 검증 함수
def try_login(input_username, input_password):
    """
    입력받은 아이디와 비밀번호가 더미 데이터와 일치하는지 확인합니다.
    """
    for user in dummy_users:
        if user["username"] == input_username:
            if user["password"] == input_password:
                print(f"🎉 로그인 성공! 환영합니다, {user['name']}님 ({user['role']})")
                return user
            else:
                print("❌ 비밀번호가 일치하지 않습니다.")
                return None
                
    print("❌ 존재하지 않는 아이디입니다.")
    return None


# --- 3. 실행 테스트 ---
if __name__ == "__main__":
    print("--- 로그인 테스트 시작 ---")
    
    # 성공 케이스
    try_login("user01", "password123!")
    
    # 비밀번호 틀린 케이스
    try_login("admin", "wrong_password")
    
    # 없는 아이디 케이스
    try_login("unknown_user", "1234")