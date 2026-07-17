from flask import Flask, request, jsonify

app = Flask(__name__)

# 1. 가상의 유저 데이터 (실제 서비스에서는 DB에서 조회합니다)
# 실무에서는 비밀번호를 절대 평문으로 저장하지 않고, 반드시 해시(암호화)해서 저장해야 합니다.
mock_user = {
    "username": "user123",
    "password": "password123"
}

# 2. 로그인 처리 API
@app.route('/login', methods=['POST'])
def login():
    # 클라이언트가 보낸 JSON 데이터 가져오기
    data = request.get_json()
    
    # 요청 데이터 검증
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({
            "success": False, 
            "message": "아이디와 비밀번호를 모두 입력해주세요."
        }), 400

    username = data['username']
    password = data['password']

    # 아이디와 비밀번호 일치 여부 확인
    if username == mock_user['username'] and password == mock_user['password']:
        return jsonify({
            "success": True, 
            "message": "로그인 성공!"
        }), 200
    else:
        return jsonify({
            "success": False, 
            "message": "아이디 또는 비밀번호가 올바르지 않습니다."
        }), 401

if __name__ == '__main__':
    # 5000번 포트에서 서버 실행
    app.run(port=5000, debug=True)