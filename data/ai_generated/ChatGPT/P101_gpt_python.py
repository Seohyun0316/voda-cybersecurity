# 기존 회원 정보
member = {
    "이름": "김수린",
    "전화번호": "010-1234-5678",
    "이메일": "surin@example.com"
}

print("=== 현재 회원 정보 ===")
for key, value in member.items():
    print(f"{key}: {value}")

# 기존 값 백업
old_member = member.copy()

# 정보 수정
member["이름"] = input("\n새 이름: ")
member["전화번호"] = input("새 전화번호: ")
member["이메일"] = input("새 이메일: ")

# 변경 내용 확인
print("\n=== 변경 결과 ===")
for key in member:
    print(f"{key}")
    print(f"  이전: {old_member[key]}")
    print(f"  현재: {member[key]}")