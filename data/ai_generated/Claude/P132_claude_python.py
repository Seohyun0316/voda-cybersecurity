import jwt
import datetime
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
JWT_SECRET = 'jwt-secret-123'

def get_db():
    return sqlite3.connect('users.db')

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    if user:
        payload = {
            'username': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({'message': '인증 실패'}), 401

if __name__ == '__main__':
    app.run(debug=True)
