def register_consultation():
    print("=" * 30)
    print("      [상담 접수 시스템]      ")
    print("=" * 30)
    
    # 1. 정보 입력 받기
    name = input("▶ 고객 이름: ").strip()
    phone = input("▶ 전화번호: ").strip()
    content = input("▶ 상담 내용: ").strip()
    
    # 입력 항목 검증 (빈칸 확인)
    if not name or not phone or not content:
        print("\n❌ 오류: 모든 항목을 올바르게 입력해주세요. 접수가 취소되었습니다.")
        return
    
    # 2. 데이터 저장 (딕셔너리 구조)
    consultation_data = {
        "이름": name,
        "전화번호": phone,
        "상담내용": content
    }
    
    # 3. 접수 내용 확인 (Print)
    print("\n" + "=" * 30)
    print("      🎉 접수가 완료되었습니다!      ")
    print("=" * 30)
    for key, value in consultation_data.items():
        print(f"• {key}: {value}")
    print("=" * 30)

# 프로그램 실행
if __name__ == "__main__":
    register_consultation()