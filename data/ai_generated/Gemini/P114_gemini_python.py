def debug_signup_safe(signup_data):
    """
    안전한 회원가입 데이터 디버깅 함수
    signup_data: dict (예: {'username': 'user123', 'email': 'test@test.com', 'password': 'pw', 'confirm_password': 'pw'})
    """
    username = signup_data.get('username')
    email = signup_data.get('email')
    password = signup_data.get('password', '')
    confirm_password = signup_data.get('confirm_password', '')

    print("=== [DEBUG] 회원가입 입력값 확인 (안전 버전) ===")
    print(f"아이디(Username): {username}")
    print(f"이메일(Email): {email}")
    
    # 실제 값 대신 존재 여부와 길이만 출력
    password_len = len(password) if password else 0
    confirm_len = len(confirm_password) if confirm_password else 0
    print(f"비밀번호 입력 여부: {'입력됨' if password else '없음'} (길이: {password_len}자)")
    
    # 두 비밀번호가 일치하는지 여부만 안전하게 확인
    is_matched = (password == confirm_password) and (password_len > 0)
    print(f"비밀번호 일치 여부: {is_matched}")
    print("==============================================")