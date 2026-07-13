from datetime import datetime
import random

def generate_order_number():
    # 1. 현재 날짜와 시간 추출 (포맷: YYYYMMDDHHMMSS)
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # 2. 4자리의 무작위 숫자 생성 (1000 ~ 9999)
    random_digits = random.randint(1000, 9999)
    
    # 3. 날짜와 랜덤 숫자 조합
    order_number = f"{now}-{random_digits}"
    
    return order_number

# 코드 실행 및 결과 확인
new_order = generate_order_number()
print(f"생성된 주문번호: {new_order}")