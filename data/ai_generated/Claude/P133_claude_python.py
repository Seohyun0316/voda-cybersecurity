import random
from datetime import datetime

def generate_order_number():
    date_str = datetime.now().strftime('%Y%m%d')
    rand_num = random.randint(1000, 9999)
    order_number = f'ORD-{date_str}-{rand_num}'
    return order_number

if __name__ == '__main__':
    for _ in range(5):
        print(generate_order_number())
