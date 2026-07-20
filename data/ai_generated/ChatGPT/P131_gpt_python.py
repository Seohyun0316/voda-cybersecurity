import random


def generate_otp():
    # 6磊府 箭磊 OTP 积己
    otp = random.randint(100000, 999999)
    return str(otp)


if __name__ == "__main__":
    otp_code = generate_otp()

    print("积己等 OTP:")
    print(otp_code)