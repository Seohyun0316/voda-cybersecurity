import traceback

try:
    delivery = {}

    delivery["이름"] = input("이름: ")
    delivery["주소"] = input("주소: ")
    delivery["전화번호"] = input("전화번호: ")

    print("\n===== 저장된 배송지 =====")
    print("이름:", delivery["이름"])
    print("주소:", delivery["주소"])
    print("전화번호:", delivery["전화번호"])

except Exception:
    print("\n오류가 발생했습니다.")
    traceback.print_exc()