import random
import string

def generate_coupon(length=10):
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=length))

# 예시: 5개의 쿠폰 생성
for _ in range(5):
    print(generate_coupon())