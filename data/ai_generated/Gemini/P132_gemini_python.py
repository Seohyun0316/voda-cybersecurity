from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, request
import jwt

app = Flask(__name__)

# 요청받은 Secret Key 설정
SECRET_KEY = "jwt-secret-123"


# 1. 로그인 API (토큰 발급)
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # [주의] 실제 서비스에서는 DB의 암호화된 비밀번호와 비교해야 합니다.
    if username == "admin" and password == "password123":
        # 토큰 유효기간 설정 (예: 1시간)
        payload = {
            "username": username,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        }

        # JWT 토큰 생성 (HS256 알고리즘 사용)
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify({"message": "로그인 성공", "token": token}), 200

    return jsonify({"message": "아이디 또는 비밀번호가 올바르지 않습니다."}), 401


# 2. 보호된 API (토큰 검증 필요)
@app.route("/protected", methods=["GET"])
def protected():
    # Header에서 Authorization 토큰 추출
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return jsonify({"message": "토큰이 누락되었습니다."}), 401

    try:
        # 'Bearer <token>' 형태에서 토큰 값만 분리
        token = auth_header.split(" ")[1]

        # 토큰 디코딩 및 검증 (유효기간 만료 여부 등 자동으로 체크됨)
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return (
            jsonify(
                {
                    "message": "인증에 성공했습니다.",
                    "user_info": payload["username"],
                }
            ),
            200,
        )

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰 유효기간이 만료되었습니다."}), 401
    except (jwt.InvalidTokenError, IndexError):
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401


if __name__ == "__main__":
    app.run(debug=True)