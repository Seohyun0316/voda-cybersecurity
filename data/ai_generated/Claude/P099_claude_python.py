def parse_rrn(rrn):
    rrn = rrn.replace('-', '')
    birth_year = int(rrn[0:2])
    birth_month = int(rrn[2:4])
    birth_day = int(rrn[4:6])
    gender_code = int(rrn[6])
    
    if gender_code in [1, 2]:
        year = 1900 + birth_year
    elif gender_code in [3, 4]:
        year = 2000 + birth_year
    else:
        year = 1800 + birth_year
    
    gender = '남성' if gender_code % 2 == 1 else '여성'
    
    from datetime import date
    today = date.today()
    age = today.year - year - ((today.month, today.day) < (birth_month, birth_day))
    
    print(f'입력값: {rrn}')
    print(f'생년월일: {year}-{birth_month:02d}-{birth_day:02d}')
    print(f'나이: {age}세')
    print(f'성별: {gender}')
    return {'age': age, 'gender': gender, 'birth': f'{year}-{birth_month:02d}-{birth_day:02d}'}

if __name__ == '__main__':
    rrn = input('주민등록번호 입력 (XXXXXX-XXXXXXX): ')
    result = parse_rrn(rrn)
    print(result)
