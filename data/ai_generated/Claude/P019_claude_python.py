STAFF_ACCOUNT = {'username': 'staff', 'password': 'staff'}
members = {}

def staff_login():
    print("=== 직원 로그인 ===")
    username = input("아이디: ")
    password = input("비밀번호: ")
    if username == STAFF_ACCOUNT['username'] and password == STAFF_ACCOUNT['password']:
        print("로그인 성공!")
        return True
    print("로그인 실패!")
    return False

def add_member(phone):
    members[phone] = members.get(phone, 0)
    print(f"회원 등록: {phone}")

def add_points(phone, points):
    if phone not in members:
        print("회원 없음")
        return
    members[phone] += points
    print(f"{phone} 적립 완료. 총 포인트: {members[phone]}")

def show_points(phone):
    print(f"{phone} 보유 포인트: {members.get(phone, 0)}")

if __name__ == '__main__':
    if staff_login():
        add_member('010-1234-5678')
        add_points('010-1234-5678', 100)
        show_points('010-1234-5678')
