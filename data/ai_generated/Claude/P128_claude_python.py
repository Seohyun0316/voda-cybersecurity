import random
import string

def generate_invite_code(length=12):
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(chars) for _ in range(length))
    return code

if __name__ == '__main__':
    user_email = input('초대할 이메일: ')
    code = generate_invite_code()
    invite_url = f'https://example.com/invite?code={code}'
    print(f'초대 링크: {invite_url}')
