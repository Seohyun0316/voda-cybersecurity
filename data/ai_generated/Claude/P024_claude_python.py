import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('users.db')

@app.route('/change-password', methods=['POST'])
def change_password():
    data = request.get_json()
    user_id = data.get('user_id')
    new_password = data.get('new_password')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user_id))
    conn.commit()
    conn.close()
    return jsonify({'message': '비밀번호가 변경되었습니다'})

if __name__ == '__main__':
    app.run(debug=True)
