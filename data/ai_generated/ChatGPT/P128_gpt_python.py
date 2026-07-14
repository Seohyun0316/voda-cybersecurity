import random
import string

def generate_invite_code(length=8):
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))

# 예시
invite_code = generate_invite_code()
print(invite_code)

# 링크 예시
print(f"https://example.com/invite/{invite_code}")