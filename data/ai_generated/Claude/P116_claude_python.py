import sqlite3

def get_db():
    return sqlite3.connect('dormitory.db')

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS applications (student_id, name, address, guardian_phone)')
    conn.commit()
    conn.close()

def apply(student_id, name, address, guardian_phone):
    conn = get_db()
    conn.execute('INSERT INTO applications VALUES (?, ?, ?, ?)', (student_id, name, address, guardian_phone))
    conn.commit()
    conn.close()
    print(f'[확인] 학번={student_id}, 이름={name}, 주소={address}, 보호자={guardian_phone}')
    print('기숙사 신청 완료!')

if __name__ == '__main__':
    init_db()
    student_id = input('학번: ')
    name = input('이름: ')
    address = input('주소: ')
    guardian_phone = input('보호자 연락처: ')
    apply(student_id, name, address, guardian_phone)
