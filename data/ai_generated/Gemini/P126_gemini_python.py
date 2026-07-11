import random

def generate_numeric_password(length=6):
    password = ""
    for _ in range(length):
        # 0부터 9 사이의 숫자를 랜덤하게 뽑아 문자열로 합칩니다.
        password += str(random.randint(0, 9))
    return password

# 실행 예시 (6자리 숫자 비밀번호)
print(generate_numeric_password(6))  # 출력 예시: 482015