import sqlite3
import hashlib

def get_db():
    return sqlite3.connect('users.db')

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def register(username, password):
    conn = get_db()
    hashed = hash_password(password)
    conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed))
    conn.commit()
    conn.close()
    print(f'회원가입 완료: {username}')

def login(username, password):
    conn = get_db()
    hashed = hash_password(password)
    row = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (username, hashed)).fetchone()
    conn.close()
    return row is not None

if __name__ == '__main__':
    init_db()
    register('testuser', 'pass1234')
    print('로그인 성공:', login('testuser', 'pass1234'))
    print('로그인 실패:', login('testuser', 'wrongpass'))
