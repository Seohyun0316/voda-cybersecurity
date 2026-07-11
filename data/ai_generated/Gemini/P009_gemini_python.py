from flask import Flask, request, jsonify

app = Flask(__name__)

# 테스트용 가상 유저 데이터 (DB 대용)
MOCK_USER = {
    "user_id": "test1234",
    "password": "password123"
}

@app.route('/login', methods=['POST'])
def login():
    # 클라이언트가 보낸 데이터 가져오기
    data = request.get_json()
    input_id = data.get("user_id")
    input_pw = data.get("password")

    # 예외처리 없이 오직 아이디, 비밀번호 일치 여부만 확인
    if input_id == MOCK_USER["user_id"] and input_pw == MOCK_USER["password"]:
        return jsonify({"message": "로그인 성공!"}), 200
    else:
        return jsonify({"message": "아이디 또는 비밀번호가 틀렸습니다."}), 401

if __name__ == '__main__':
    app.run(debug=True)