import random

items = [
    ("¿œπ› ∞À", 70),
    ("»Ò±Õ πÊ∆–", 25),
    ("¿¸º≥ ∞©ø ", 5)
]

def draw_item():
    rand = random.randint(1, 100)

    total = 0
    for item, chance in items:
        total += chance
        if rand <= total:
            return item

# ªÃ±‚ 5»∏
for i in range(5):
    print(f"{i+1}»∏ ªÃ±‚ ∞·∞˙:", draw_item())