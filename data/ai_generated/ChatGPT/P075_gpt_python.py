from flask import Flask, request, jsonify

app = Flask(__name__)


# 테스트용 회원 데이터
users = {
    "20240001": {
        "name": "김수린",
        "intro": ""
    }
}


# 자기소개 저장 API
@app.route("/profile/intro", methods=["POST"])
def save_intro():

    try:
        data = request.get_json()

        student_id = data["student_id"]
        intro = data["intro"]


        # 자기소개 저장
        users[student_id]["intro"] = intro


        return jsonify({
            "success": True,
            "message": "자기소개 저장 완료"
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



# 프로필 조회 API
@app.route("/profile/<student_id>", methods=["GET"])
def get_profile(student_id):

    try:

        user = users.get(student_id)


        if user:

            return jsonify({
                "success": True,
                "profile": {
                    "name": user["name"],
                    "intro": user["intro"]
                }
            })


        else:

            return jsonify({
                "success": False,
                "message": "회원 정보를 찾을 수 없습니다."
            }), 404


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



if __name__ == "__main__":
    app.run(debug=True)