import random

def generate_auth_code():
    code = random.randint(100000, 999999)
    return str(code)

if __name__ == '__main__':
    email = input('이메일 주소: ')
    code = generate_auth_code()
    print(f'{email}로 인증번호 발송: {code}')
