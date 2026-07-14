from flask import Flask, request, jsonify
import jwt
import datetime

app = Flask(__name__)


# JWT Secret Key
SECRET_KEY = "jwt-secret-123"


# 테스트 사용자
users = {
    "admin": {
        "password": "1234",
        "name": "관리자"
    }
}


# 로그인 API
@app.route("/login", methods=["POST"])
def login():

    try:
        data = request.get_json()

        username = data["username"]
        password = data["password"]


        user = users.get(username)


        # 사용자 확인
        if user is None or user["password"] != password:
            return jsonify({
                "success": False,
                "message": "아이디 또는 비밀번호가 틀렸습니다."
            }), 401


        # JWT 생성
        token = jwt.encode(
            {
                "username": username,
                "name": user["name"],
                "exp": datetime.datetime.utcnow()
                     + datetime.timedelta(hours=1)
            },
            SECRET_KEY,
            algorithm="HS256"
        )


        return jsonify({
            "success": True,
            "message": "로그인 성공",
            "token": token
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



# JWT 인증 테스트 API
@app.route("/mypage", methods=["GET"])
def mypage():

    try:

        token = request.headers.get("Authorization")


        if not token:
            return jsonify({
                "message": "토큰이 없습니다."
            }), 401


        # Bearer 제거
        token = token.replace("Bearer ", "")


        # 토큰 검증
        decoded = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"]
        )


        return jsonify({
            "success": True,
            "user": decoded
        })


    except jwt.ExpiredSignatureError:

        return jsonify({
            "success": False,
            "message": "토큰이 만료되었습니다."
        }), 401


    except jwt.InvalidTokenError:

        return jsonify({
            "success": False,
            "message": "유효하지 않은 토큰입니다."
        }), 401



if __name__ == "__main__":
    app.run(debug=True)