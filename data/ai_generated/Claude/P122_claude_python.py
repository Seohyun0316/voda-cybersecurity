import random
import string

def generate_reset_token(length=32):
    chars = string.ascii_letters + string.digits
    token = ''.join(random.choice(chars) for _ in range(length))
    return token

if __name__ == '__main__':
    token = generate_reset_token()
    print(f'비밀번호 재설정 토큰: {token}')
