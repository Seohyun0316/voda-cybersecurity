from datetime import datetime

def analyze_rrn(rrn_input):
    # 공백 및 하이픈 제거
    rrn = rrn_input.replace(" ", "").replace("-", "")
    
    # 유효성 기본 검사 (13자리 숫자인지 확인)
    if len(rrn) != 13 or not rrn.isdigit():
        return "올바른 주민등록번호 형식이 아닙니다. (하이픈 제외 13자리 숫자)"
    
    # 앞자리(생년월일), 뒷자리 첫 번째 숫자 분리
    birth_part = rrn[:6]
    gender_digit = int(rrn[6])
    
    # 뒷자리 첫 번째 숫자로 출생 연도 세기(Century) 및 성별 판별
    # 1, 2: 1900년대생 / 3, 4: 2000년대생 / 9, 0: 1800년대생 / 5, 6, 7, 8: 외국인
    if gender_digit in [1, 2, 5, 6]:
        century = 1900
    elif gender_digit in [3, 4, 7, 8]:
        century = 2000
    elif gender_digit in [9, 0]:
        century = 1800
    else:
        return "유효하지 않은 주민등록번호 뒷자리입니다."
    
    # 성별 판별 (홀수는 남성, 짝수는 여성)
    gender = "남성" if gender_digit % 2 != 0 else "여성"
    
    # 생년월일 추출
    year = century + int(birth_part[0:2])
    month = int(birth_part[2:4])
    day = int(birth_part[4:6])
    
    # 날짜 유효성 검사
    try:
        birth_date = datetime(year, month, day)
    except ValueError:
        return "주민등록번호에 포함된 날짜가 유효하지 않습니다."
        
    # 현재 날짜 기준 나이 계산
    today = datetime.today()
    
    # 1. 만 나이 계산
    american_age = today.year - birth_date.year
    # 생일이 아직 지나지 않았다면 1을 뺌
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        american_age -= 1
        
    # 2. 연 나이 계산 (현재 연도 - 출생 연도)
    year_age = today.year - birth_date.year
    
    # 결과 출력 형식 맞추기 (마스킹 처리 포함)
    masked_input = f"{rrn_input[:6]}-{rrn_input[7] if '-' in rrn_input else rrn_input[6]}******"

    return {
        "입력값": masked_input,
        "생년월일": birth_date.strftime("%Y년 %m월 %d일"),
        "성별": gender,
        "만 나이": f"{american_age}세",
        "연 나이": f"{year_age}세"
    }

# --- 실행 테스트 ---
# 테스트용 예시 입력 (실제 주민등록번호가 아닌 가상의 예시입니다)
sample_input = "050515-3123456" 
result = analyze_rrn(sample_input)

if isinstance(result, dict):
    print("====== 분석 결과 ======")
    for key, value in result.items():
        print(f"■ {key}: {value}")
else:
    print(result)