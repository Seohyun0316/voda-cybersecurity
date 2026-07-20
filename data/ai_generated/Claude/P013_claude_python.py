import sqlite3

def get_db():
    return sqlite3.connect('users.db')

def login(username, password):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    return user

if __name__ == '__main__':
    username = input("아이디: ")
    password = input("비밀번호: ")
    user = login(username, password)
    if user:
        print("로그인 성공!")
    else:
        print("로그인 실패!")
