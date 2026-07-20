from flask import Flask, request, jsonify, session
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "change-this-secret"

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data["email"]
    password = data["password"]

    # 이메일로 사용자 조회
    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"message": "이메일 또는 비밀번호가 올바르지 않습니다."}), 401

    if not check_password_hash(user.password, password):
        return jsonify({"message": "이메일 또는 비밀번호가 올바르지 않습니다."}), 401

    # 로그인 성공
    session["user_id"] = user.id
    session["user_name"] = user.name

    return jsonify({
        "message": "로그인 성공",
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }
    }), 200