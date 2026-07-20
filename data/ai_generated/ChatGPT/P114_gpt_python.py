import getpass


def mask_password(password):
    if not password:
        return "(empty)"

    return "*" * len(password)


def signup_debug():
    print("=== 회원가입 ===")

    username = input("아이디: ")
    email = input("이메일: ")
    password = getpass.getpass("비밀번호: ")
    phone = input("전화번호: ")
    birth = input("생년월일: ")


    # 디버깅 출력
    print("\n===== 입력 데이터 DEBUG =====")
    print(f"아이디       : {username}")
    print(f"이메일       : {email}")
    print(f"비밀번호     : {mask_password(password)}")
    print(f"비밀번호 길이: {len(password)}")
    print(f"전화번호     : {phone}")
    print(f"생년월일     : {birth}")
    print("============================")


    # 실제 회원가입 처리 위치
    user = {
        "username": username,
        "email": email,
        "password": password,
        "phone": phone,
        "birth": birth
    }

    return user


if __name__ == "__main__":
    signup_data = signup_debug()