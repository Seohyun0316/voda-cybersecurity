import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('users.db')

@app.route('/profile/update', methods=['POST'])
def update_profile():
    data = request.get_json()
    user_id = data.get('user_id')
    field = data.get('field')
    new_value = data.get('new_value')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f'SELECT {field} FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    old_value = row[0] if row else None
    cursor.execute(f'UPDATE users SET {field} = ? WHERE id = ?', (new_value, user_id))
    conn.commit()
    conn.close()
    print(f'[회원정보 수정] user_id={user_id}, field={field}, 이전={old_value}, 새값={new_value}')
    return jsonify({'message': '수정 완료', 'old': old_value, 'new': new_value})

if __name__ == '__main__':
    app.run(debug=True)
