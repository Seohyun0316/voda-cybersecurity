import random

items = [
    {'name': '전설 검', 'grade': 'SSR', 'rate': 0.01},
    {'name': '희귀 방패', 'grade': 'SR', 'rate': 0.05},
    {'name': '고급 갑옷', 'grade': 'R', 'rate': 0.14},
    {'name': '일반 포션', 'grade': 'N', 'rate': 0.80},
]

def gacha():
    r = random.random()
    cumulative = 0
    for item in items:
        cumulative += item['rate']
        if r <= cumulative:
            return item
    return items[-1]

if __name__ == '__main__':
    n = int(input('뽑기 횟수: '))
    results = {}
    for _ in range(n):
        item = gacha()
        results[item['name']] = results.get(item['name'], 0) + 1
    for name, count in results.items():
        print(f'{name}: {count}개')
