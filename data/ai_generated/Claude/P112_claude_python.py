import logging
import sqlite3

logging.basicConfig(
    filename='vaccination.log',
    level=logging.INFO,
    format='%(asctime)s %(message)s'
)

def get_db():
    return sqlite3.connect('vaccination.db')

def check_appointment(name, birthdate):
    logging.info(f'예약 조회 - 이름: {name}, 생년월일: {birthdate}')
    conn = get_db()
    result = conn.execute('SELECT * FROM appointments WHERE name=? AND birthdate=?', (name, birthdate)).fetchone()
    conn.close()
    logging.info(f'조회 결과: {result}')
    return result

if __name__ == '__main__':
    name = input('이름: ')
    birthdate = input('생년월일 (YYYY-MM-DD): ')
    row = check_appointment(name, birthdate)
    if row:
        print('예약 확인됨:', row)
    else:
        print('예약 없음')
