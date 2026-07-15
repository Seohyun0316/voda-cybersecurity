import random
import string

def generate_session_id(length=32):
    chars = string.ascii_letters + string.digits
    session_id = ''.join(random.choice(chars) for _ in range(length))
    return session_id

sessions = {}

def create_session(user_id):
    session_id = generate_session_id()
    sessions[session_id] = user_id
    return session_id

if __name__ == '__main__':
    user_id = input('사용자 ID: ')
    sid = create_session(user_id)
    print(f'세션 ID: {sid}')
