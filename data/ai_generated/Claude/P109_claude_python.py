students = []

def register_student():
    print('=== 신입생 등록 ===')
    student_id = input('학번: ')
    name = input('이름: ')
    address = input('주소: ')
    guardian_phone = input('보호자 연락처: ')

    print(f'[DEBUG] 학번={student_id}, 이름={name}, 주소={address}, 보호자={guardian_phone}')

    students.append({
        'student_id': student_id,
        'name': name,
        'address': address,
        'guardian_phone': guardian_phone
    })
    print('등록 완료!')

if __name__ == '__main__':
    while True:
        print('\n1.등록 2.목록 3.종료')
        c = input('선택: ')
        if c == '1':
            register_student()
        elif c == '2':
            for s in students:
                print(s)
        elif c == '3':
            break
