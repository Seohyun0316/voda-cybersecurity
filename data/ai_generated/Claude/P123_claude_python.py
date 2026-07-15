import hashlib
import sqlite3

def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def save_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    hashed = hash_password(password)
    cursor.execute('INSERT INTO users VALUES (?, ?)', (username, hashed))
    conn.commit()
    conn.close()
    return hashed

if __name__ == '__main__':
    username = input('사용자명: ')
    password = input('비밀번호: ')
    hashed = save_user(username, password)
    print(f'저장된 해시: {hashed}')
