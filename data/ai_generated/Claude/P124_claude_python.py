import random
import string

def generate_coupon_code(length=10):
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choice(chars) for _ in range(length))
    return code

def generate_coupons(count=10):
    return [generate_coupon_code() for _ in range(count)]

if __name__ == '__main__':
    n = int(input('생성할 쿠폰 수: '))
    coupons = generate_coupons(n)
    for c in coupons:
        print(c)
