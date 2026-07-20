users = {
    'admin': 'admin123',
    'user1': 'pass1',
    'user2': 'pass2',
    'testuser': 'test1234',
    'guest': 'guest',
}

def login(username, password):
    if users.get(username) == password:
        print(f"로그인 성공: {username}")
        return True
    print("로그인 실패")
    return False

if __name__ == '__main__':
    print("=== 로그인 테스트 ===")
    username = input("아이디: ")
    password = input("비밀번호: ")
    login(username, password)
