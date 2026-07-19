import random

# 000000부터 999999 사이의 숫자를 무작위로 생성하고, 
# 앞자리가 0일 경우 생략되지 않도록 6자리 포맷(zfill)을 지정합니다.
otp = str(random.randint(0, 999999)).zfill(6)

print(f"생성된 OTP: {otp}")