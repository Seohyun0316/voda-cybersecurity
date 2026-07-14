from datetime import date

rrn = input("주민등록번호를 입력하세요 (예: 010101-3123456): ")

# 하이픈 제거
rrn = rrn.replace("-", "")

birth = rrn[:6]
gender_code = rrn[6]

yy = int(birth[:2])
mm = int(birth[2:4])
dd = int(birth[4:6])

# 출생 연도 계산
if gender_code in ["1", "2"]:
    year = 1900 + yy
elif gender_code in ["3", "4"]:
    year = 2000 + yy
else:
    print("올바른 주민등록번호가 아닙니다.")
    exit()

# 나이 계산
today = date.today()
age = today.year - year
if (today.month, today.day) < (mm, dd):
    age -= 1

# 성별 계산
if gender_code in ["1", "3"]:
    gender = "남성"
else:
    gender = "여성"

print("\n===== 결과 =====")
print("입력한 주민등록번호:", rrn)
print("출생년도:", year)
print("나이:", age)
print("성별:", gender)