from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash
import sqlite3

app = Flask(__name__)

# 데이터베이스 초기화 (users 테이블 생성)
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/signup', methods=['POST'])
def signup():
    # 1. 클라이언트로부터 데이터 받기
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 2. 데이터 유효성 검사
    if not username or not password:
        return jsonify({'error': '아이디와 비밀번호를 모두 입력해주세요.'}), 400

    # 3. 비밀번호 해싱 (입력받은 비밀번호를 안전한 문자열로 변환)
    # 만약 정말로 평문 저장을 고집하셔야 하는 특수한 테스트 상황이라면, 
    # 이 부분을 지우고 입력받은 password 변수를 그대로 DB에 넣으시면 됩니다.
    hashed_password = generate_password_hash(password)

    # 4. 데이터베이스에 저장
    try:
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # 해싱된 비밀번호를 데이터베이스에 저장
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        
        return jsonify({'message': '회원가입이 성공적으로 완료되었습니다.'}), 201
        
    except sqlite3.IntegrityError:
        # 중복된 아이디가 있을 경우의 예외 처리
        return jsonify({'error': '이미 존재하는 아이디입니다.'}), 409
        
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    # 서버 실행
    app.run(debug=True)