import random

def generate_otp(digits=6):
    otp = random.randint(10**(digits-1), 10**digits - 1)
    return str(otp)

if __name__ == '__main__':
    otp = generate_otp()
    print(f'OTP: {otp}')
