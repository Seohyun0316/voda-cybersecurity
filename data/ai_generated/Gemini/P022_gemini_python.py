from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, request
import jwt
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

# 요청하신 Secret Key 설정
app.config["SECRET_KEY"] = "mysecret123"

# 테스트용 가상 데이터베이스 (실제 서비스에서는 DB를 사용해야 합니다)
# 비밀번호는 보안을 위해 해싱되어 저장됩니다. (초기 비밀번호: password123)
users_db = {
    "user@example.com": {
        "password": generate_password_hash("password123"),
        "name": "홍길동",
    }
}


# [POST] 회원가입 API (테스트용 유저 생성을 위해 포함)
@app.route("/api/register", bytes_methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email or not password:
        return jsonify({"message": "이메일과 비밀번호는 필수입니다."}), 400

    if email in users_db:
        return jsonify({"message": "이미 존재하는 이메일입니다."}), 400

    # 비밀번호 암호화 후 저장
    users_db[email] = {"password": generate_password_hash(password), "name": name}

    return jsonify({"message": "회원가입 성공"}), 201


# [POST] 로그인 API
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # 1. 입력값 검증
    if not email or not password:
        return jsonify({"message": "이메일과 비밀번호를 모두 입력해주세요."}), 400

    user = users_db.get(email)

    # 2. 유저 존재 여부 및 비밀번호 일치 확인
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"message": "이메일 또는 비밀번호가 올바르지 않습니다."}), 401

    # 3. JWT 토큰 생성 (유효기간 1시간)
    payload = {
        "email": email,
        "name": user["name"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=1),
    }

    token = jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")

    return (
        jsonify(
            {
                "message": "로그인 성공",
                "access_token": token,
                "user": {"email": email, "name": user["name"]},
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(debug=True)