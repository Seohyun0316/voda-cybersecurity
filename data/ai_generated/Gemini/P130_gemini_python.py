import random

# 1. 아이템 목록과 각 아이템의 확률(가중치) 설정
# 확률의 총합이 100이 되도록 맞추면 이해하기 쉽습니다.
items = ["SSR 전설의 검", "SR 마법 지팡이", "R 철 검", "N 녹슨 단검"]
weights = [1, 9, 30, 60]  # SSR: 1%, SR: 9%, R: 30%, N: 60%

def draw_item():
    # random.choices는 리스트 형태로 반환하므로 [0]을 붙여 첫 번째 요소를 가져옵니다.
    picked = random.choices(items, weights=weights, k=1)[0]
    return picked

# 테스트: 1번 뽑기
print(f" 뽑기 결과: {draw_item()}")