import sqlite3

def get_birthday_targets():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, email, phone, birthdate FROM users WHERE strftime("%m-%d", birthdate) = strftime("%m-%d", "now")')
    users = cursor.fetchall()
    conn.close()
    print('=== 오늘 생일 대상자 ===')
    for user in users:
        print(f'이름: {user[0]}, 이메일: {user[1]}, 전화: {user[2]}, 생일: {user[3]}')
    return users

if __name__ == '__main__':
    get_birthday_targets()
