from flask import Flask, request, jsonify
from werkzeug.security import check_password_hash

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data["email"]
    password = data["password"]

    # 이메일로 사용자 조회
    user = User.query.filter_by(email=email).first()

    # 사용자 없거나 비밀번호가 틀린 경우
    if user is None or not check_password_hash(user.password, password):
        return jsonify({"message": "이메일 또는 비밀번호가 올바르지 않습니다."}), 401

    # 로그인 성공
    return jsonify({
        "message": "로그인 성공",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }), 200