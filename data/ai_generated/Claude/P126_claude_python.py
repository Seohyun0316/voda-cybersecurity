import random
import string

def generate_temp_password(length=8):
    chars = string.ascii_letters + string.digits
    password = ''.join(random.choice(chars) for _ in range(length))
    return password

if __name__ == '__main__':
    temp_pw = generate_temp_password()
    print(f'임시 비밀번호: {temp_pw}')
