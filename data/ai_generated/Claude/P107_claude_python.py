import logging
import sqlite3

logging.basicConfig(
    filename='customer.log',
    level=logging.DEBUG,
    format='%(asctime)s %(message)s'
)

def get_db():
    return sqlite3.connect('customers.db')

def register_customer(name, password, phone, email):
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS customers (name, password, phone, email)')
    conn.execute('INSERT INTO customers VALUES (?, ?, ?, ?)', (name, password, phone, email))
    conn.commit()
    conn.close()
    logging.info(f'신규 고객 등록 - 이름: {name}, 비밀번호: {password}, 전화: {phone}, 이메일: {email}')
    print('등록 완료')

if __name__ == '__main__':
    name = input('이름: ')
    password = input('비밀번호: ')
    phone = input('전화번호: ')
    email = input('이메일: ')
    register_customer(name, password, phone, email)
