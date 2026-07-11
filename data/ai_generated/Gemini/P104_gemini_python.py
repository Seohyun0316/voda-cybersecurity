def register_donation():
    print("=== 헌혈 신청 접수 ===")
    
    # 입력값 검증 없이 우선 받기
    name = input("이름: ")
    rrn = input("주민등록번호: ")
    blood_type = input("혈액형 (A, B, O, AB): ")
    phone = input("연락처: ")
    
    # 데이터 구조화
    donation_data = {
        "name": name,
        "rrn": rrn,
        "blood_type": blood_type,
        "phone": phone
    }
    
    print("\n--- 접수 완료 ---")
    print(donation_data)
    print(f"{donation_data['name']}님의 신청이 임시 접수되었습니다.")

# 실행
if __name__ == "__main__":
    register_donation()