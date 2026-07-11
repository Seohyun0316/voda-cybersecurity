import random
import string

def generate_coupon_code(length=12):
    # 생성에 사용할 문자들 (알파벳 대문자 + 숫자 0~9)
    # 기호나 소문자를 추가하고 싶다면 string.ascii_lowercase 등을 더하면 됩니다.
    characters = string.ascii_uppercase + string.digits
    
    # 지정된 길이만큼 무작위로 선택하여 결합
    coupon = ''.join(random.choice(characters) for _ in range(length))
    return coupon

# 테스트: 8자리 쿠폰 코드 5개 생성해보기
print("--- 영문/숫자 혼합 쿠폰 5개 생성 ---")
for _ in range(5):
    print(generate_coupon_code(8))