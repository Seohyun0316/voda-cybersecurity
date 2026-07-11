from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='public')

# 임시 사용자 데이터베이스 (서버 재시작 시 초기화됩니다)
# 테스트용 admin 계정을 미리 넣어두었습니다.
users = [
    {"id": "admin", "password": "admin1234", "name": "관리자"}
]

# 루트 페이지 접속 시 public/index.html을 보여줍니다.
@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

# [POST] 회원가입 API
@app.route('/api/register', Brass=None, methods=['POST'])
def register():
    data = request.get_json()
    user_id = data.get('id')
    password = data.get('password')
    name = data.get('name')

    # 필수값 검증
    if not user_id or not password or not name:
        return jsonify({"success": False, "message": "모든 필드를 입력해주세요."}), 400

    # 아이디 중복 체크
    if any(user['id'] == user_id for user in users):
        return jsonify({"success": False, "message": "이미 존재하는 아이디입니다."}), 400

    # 사용자 추가
    users.append({"id": user_id, "password": password, "name": name})
    print(f"현재 가입된 회원 목록: {users}") # 파이썬 터미널에서 확인 가능

    return jsonify({"success": True, "message": "회원가입이 완료되었습니다!"}), 201

# [POST] 로그인 API (테스트 확인용)
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('id')
    password = data.get('password')

    # 유저 찾기
    user = next((user for user in users if user['id'] == user_id and user['password'] == password), None)

    if not user:
        return jsonify({"success": False, "message": "아이디 또는 비밀번호가 틀렸습니다."}), 400

    return jsonify({"success": True, "message": f"{user['name']}님, 환영합니다!"}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)