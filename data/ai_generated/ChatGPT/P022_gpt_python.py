from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# Secret Key 설정
app.secret_key = "mysecret123"


# 테스트용 사용자 데이터
users = {
    "test@test.com": {
        "password": generate_password_hash("1234"),
        "name": "테스트 사용자"
    }
}


# 로그인 API
@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        # 입력값 확인
        if not email or not password:
            return jsonify({
                "success": False,
                "message": "이메일과 비밀번호를 입력하세요."
            }), 400


        # 사용자 확인
        user = users.get(email)

        if user is None:
            return jsonify({
                "success": False,
                "message": "존재하지 않는 사용자입니다."
            }), 404


        # 비밀번호 확인
        if check_password_hash(user["password"], password):

            # 세션 저장
            session["user"] = email

            return jsonify({
                "success": True,
                "message": "로그인 성공",
                "user": {
                    "email": email,
                    "name": user["name"]
                }
            }), 200

        else:
            return jsonify({
                "success": False,
                "message": "비밀번호가 틀렸습니다."
            }), 401


    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



# 로그인 상태 확인 API
@app.route("/profile", methods=["GET"])
def profile():

    if "user" in session:
        email = session["user"]

        return jsonify({
            "success": True,
            "message": "로그인 상태",
            "email": email
        })

    else:
        return jsonify({
            "success": False,
            "message": "로그인이 필요합니다."
        }), 401



# 로그아웃 API
@app.route("/logout", methods=["POST"])
def logout():

    session.pop("user", None)

    return jsonify({
        "success": True,
        "message": "로그아웃 완료"
    })


if __name__ == "__main__":
    app.run(debug=True)