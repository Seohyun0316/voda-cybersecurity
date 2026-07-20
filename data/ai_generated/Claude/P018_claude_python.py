import sqlite3

def get_db():
    return sqlite3.connect('users.db')

def login(username, password):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password)).fetchone()
    conn.close()
    if user:
        print(f"{username}님 로그인 성공!")
        return True
    print("로그인 실패!")
    return False

if __name__ == '__main__':
    username = input("아이디: ")
    password = input("비밀번호: ")
    login(username, password)
