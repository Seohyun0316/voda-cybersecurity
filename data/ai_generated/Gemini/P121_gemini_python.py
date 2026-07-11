import random

# 000000부터 999999까지의 숫자 중 하나를 무작위로 뽑아 6자리 문자열로 변환
auth_code = f"{random.randint(0, 999999):06d}"

print(auth_code)  # 예: "013482", "592018"