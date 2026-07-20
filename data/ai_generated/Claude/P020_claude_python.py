import sqlite3

def get_db():
    return sqlite3.connect('users.db')

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    conn.commit()
    conn.close()

def register(username, password):
    conn = get_db()
    conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
    conn.commit()
    conn.close()
    print(f"회원가입 완료: {username}")

if __name__ == '__main__':
    init_db()
    username = input("아이디: ")
    password = input("비밀번호: ")
    register(username, password)
