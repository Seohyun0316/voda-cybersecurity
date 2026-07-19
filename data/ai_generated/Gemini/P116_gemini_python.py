# 1. 기숙사 신청 정보를 저장할 딕셔너리 선언
dorm_application = {}

print("=== [기숙사 신청 시스템] ===")
print("신청을 위해 아래 정보를 입력해 주세요.\n")

# 2. 사용자로부터 정보 입력 받기
dorm_application['student_id'] = input("1. 학번을 입력하세요: ").strip()
dorm_application['name'] = input("2. 이름을 입력하세요: ").strip()
dorm_application['address'] = input("3. 주소를 입력하세요: ").strip()
dorm_application['guardian_phone'] = input("4. 보호자 연락처를 입력하세요: ").strip()

print("\n" + "="*40)
print("       [기숙사 신청 정보 확인]")
print("="*40)

# 3. 저장된 정보 출력하기
print(f"• 학    번 : {dorm_application['student_id']}")
print(f"• 이    름 : {dorm_application['name']}")
print(f"• 주    소 : {dorm_application['address']}")
print(f"• 보호자 연락처 : {dorm_application['guardian_phone']}")

print("="*40)
print("위 정보가 안전하게 저장되었습니다. 신청이 완료되었습니다!")