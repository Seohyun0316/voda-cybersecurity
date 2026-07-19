import json
import os

# 데이터 파일 경로
DATA_FILE = "customers.json"

# 회원 데이터 로드
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# 회원 데이터 저장
def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# 직원 로그인 기능
def staff_login():
    print("\n" + "="*30)
    print("      CAFE SYSTEM LOGIN      ")
    print("="*30)
    attempts = 3
    while attempts > 0:
        username = input("직원 ID: ").strip()
        password = input("비밀번호: ").strip()
        
        if username == "staff" and password == "staff":
            print("\n[로그인 성공] 반갑습니다, 직원님!")
            return True
        else:
            attempts -= 1
            print(f"[오류] ID 또는 비밀번호가 틀렸습니다. (남은 기회: {attempts}회)")
    
    print("\n[로그인 실패] 3회 오류로 프로그램을 종료합니다.")
    return False

# 신규 회원 등록
def register_customer(data):
    print("\n--- 신규 회원 등록 ---")
    phone = input("전화번호 입력 (예: 01012345678): ").strip()
    
    if phone in data:
        print("[안내] 이미 등록된 회원입니다.")
        return
    
    name = input("회원 이름 입력: ").strip()
    data[phone] = {
        "name": name,
        "stamps": 0,
        "coupons": 0
    }
    save_data(data)
    print(f"\n[등록 완료] {name} 회원님이 등록되었습니다!")

# 스탬프 적립
def accumulate_stamps(data):
    print("\n--- 스탬프 적립 ---")
    phone = input("회원 전화번호 입력: ").strip()
    
    if phone not in data:
        print("[오류] 등록되지 않은 회원입니다. 먼저 회원을 등록해주세요.")
        return
        
    try:
        count = int(input("적립할 음료 수량: "))
        if count <= 0:
            print("[오류] 1개 이상의 수량을 입력해주세요.")
            return
    except ValueError:
        print("[오류] 숫자만 입력 가능합니다.")
        return
    
    customer = data[phone]
    customer["stamps"] += count
    print(f"\n[적립 완료] 스탬프 {count}개가 적립되었습니다.")
    
    # 10개당 쿠폰 1개로 전환 (남은 스탬프는 이월)
    if customer["stamps"] >= 10:
        new_coupons = customer["stamps"] // 10
        customer["coupons"] += new_coupons
        customer["stamps"] %= 10
        print(f"🎉 축하합니다! 스탬프 10개를 모아 무료 음료 쿠폰 {new_coupons}장이 발급되었습니다!")
        
    save_data(data)
    print(f"현황 - {customer['name']}님 | 남은 스탬프: {customer['stamps']}개 | 보유 쿠폰: {customer['coupons']}장")

# 회원 조회
def search_customer(data):
    print("\n--- 회원 조회 ---")
    search_query = input("조회할 전화번호 (뒷자리 입력 가능): ").strip()
    
    found = False
    for phone, info in data.items():
        if search_query in phone:
            print(f"\n[조회 결과]")
            print(f"이름: {info['name']}")
            print(f"연락처: {phone}")
            print(f"스탬프: {info['stamps']} / 10")
            print(f"보유 쿠폰: {info['coupons']}장")
            print("-" * 20)
            found = True
            
    if not found:
        print("[안내] 일치하는 회원이 없습니다.")

# 메인 메뉴 시스템
def main():
    customers = load_data()
    
    # 프로그램 시작 시 로그인 요구
    if not staff_login():
        return
        
    while True:
        print("\n" + "="*30)
        print("      CAFE 적립 시스템      ")
        print("="*30)
        print("1. 신규 회원 등록")
        print("2. 스탬프 적립")
        print("3. 회원 정보 조회")
        print("4. 프로그램 종료")
        print("="*30)
        
        choice = input("원하는 메뉴 번호를 선택하세요: ").strip()
        
        if choice == "1":
            register_customer(customers)
        elif choice == "2":
            accumulate_stamps(customers)
        elif choice == "3":
            search_customer(customers)
        elif choice == "4":
            print("\n[시스템 종료] 프로그램을 안전하게 종료합니다. 이용해 주셔서 감사합니다.")
            break
        else:
            print("[오류] 올바른 번호를 선택해 주세요 (1~4).")

if __name__ == "__main__":
    main()