applicants = []

def apply(name, phone):
    applicants.append({'name': name, 'phone': phone})
    print(f'응모 완료: {name}')

def show_all():
    print('=== 응모자 목록 ===')
    for a in applicants:
        print(f"이름: {a['name']}, 전화: {a['phone']}")

if __name__ == '__main__':
    while True:
        print('\n1.응모 2.목록 3.종료')
        choice = input('선택: ')
        if choice == '1':
            name = input('이름: ')
            phone = input('전화번호: ')
            apply(name, phone)
        elif choice == '2':
            show_all()
        elif choice == '3':
            break
