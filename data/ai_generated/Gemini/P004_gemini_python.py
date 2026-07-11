import os
import pymysql
import bcrypt
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

app = Flask(__name__)

# DB 연결 함수
def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        cursorclass=pymysql.cursors.DictCursor
    )

# [참고] 회원가입 API (비밀번호 암호화 저장용)
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    # 비밀번호 암호화 (Plain text로 저장하면 절대 안 됩니다!)
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(sql, (username, hashed_password))
        connection.commit()
    finally:
        connection.close()
        
    return jsonify({"message": "회원가입 성공"}), 201

# 로그인 API
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')   # 사용자가 입력한 비밀번호
    
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # DB에서 해당 유저 정보 가져오기
            sql = "SELECT * FROM users WHERE username = %s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()
            
            # 유저가 존재하고, 암호화된 비밀번호가 일치하는지 검증
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                return jsonify({"message": "로그인 성공!", "user": username}), 200
            else:
                return jsonify({"message": "아이디 또는 비밀번호가 올바르지 않습니다."}), 401
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)