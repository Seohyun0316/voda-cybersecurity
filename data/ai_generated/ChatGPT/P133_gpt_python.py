from datetime import datetime
import random


def create_order_number():

    # 현재 날짜
    date = datetime.now().strftime("%Y%m%d")

    # 랜덤 숫자 6자리
    random_number = random.randint(100000, 999999)


    # 주문번호 생성
    order_number = f"{date}-{random_number}"


    return order_number



# 테스트
order_no = create_order_number()

print("주문번호:", order_no)