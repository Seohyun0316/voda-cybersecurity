import sqlite3

def get_db():
    return sqlite3.connect('membership.db')

def get_points(phone):
    conn = get_db()
    query = f"SELECT * FROM members WHERE phone = '{phone}'"
    print(f'[쿼리] {query}')
    result = conn.execute(query).fetchone()
    conn.close()
    print(f'[결과] {result}')
    return result

if __name__ == '__main__':
    phone = input('전화번호: ')
    row = get_points(phone)
    if row:
        print(f'포인트: {row[-1]}')
    else:
        print('회원 정보 없음')
