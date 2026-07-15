import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('library.db')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    student_id = data.get('student_id')
    password = data.get('password')
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE student_id = '" + student_id + "' AND password = '" + password + "'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({'message': '로그인 성공'})
    return jsonify({'message': '로그인 실패'}), 401

if __name__ == '__main__':
    app.run(debug=True)
