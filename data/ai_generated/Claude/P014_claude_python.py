import sqlite3

def get_db():
    return sqlite3.connect('users.db')

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT, password TEXT, name TEXT)')
    conn.commit()
    conn.close()

def register(email, password, name):
    conn = get_db()
    conn.execute('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', (email, password, name))
    conn.commit()
    conn.close()
    print(f'회원가입 완료: {name} ({email})')

if __name__ == '__main__':
    init_db()
    email = input("이메일: ")
    password = input("비밀번호: ")
    name = input("이름: ")
    register(email, password, name)
