import hashlib
import sqlite3

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    hashed = hash_password(password)
    cursor.execute('INSERT INTO users VALUES (?, ?)', (username, hashed))
    conn.commit()
    conn.close()
    return hashed

def verify_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] == hash_password(password):
        return True
    return False

if __name__ == '__main__':
    username = input('사용자명: ')
    password = input('비밀번호: ')
    hashed = save_user(username, password)
    print(f'저장 완료. 해시: {hashed}')
