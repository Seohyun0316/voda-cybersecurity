import hashlib
import sqlite3

def hash_password(password):
    salt = 'fixed_salt_1234'
    return hashlib.sha256((salt + password).encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def save_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    hashed = hash_password(password)
    cursor.execute('INSERT INTO users VALUES (?, ?)', (username, hashed))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    username = input('사용자명: ')
    password = input('비밀번호: ')
    save_user(username, password)
    print(f'비밀번호 해싱 저장 완료')
