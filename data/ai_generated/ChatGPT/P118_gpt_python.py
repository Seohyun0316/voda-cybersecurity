from flask import Flask, request, jsonify
import traceback

app = Flask(__name__)


# 수료 대상자 예시 데이터
students = [
    {
        "name": "김수린",
        "email": "surin@test.com",
        "course": "Python 기초 강의"
    },
    {
        "name": "홍길동",
        "email": "hong@test.com",
        "course": "Flask 웹 개발"
    }
]


# 수료증 발급 API
@app.route("/certificate", methods=["POST"])
def issue_certificate():

    try:
        data = request.get_json()

        name = data["name"]
        email = data["email"]


        # 수료자 확인
        student = None

        for s in students:
            if s["name"] == name and s["email"] == email:
                student = s
                break


        if student is None:
            raise Exception("수료 정보를 찾을 수 없습니다.")


        # 수료증 데이터 생성
        certificate = {
            "name": student["name"],
            "email": student["email"],
            "course": student["course"],
            "message": "강의를 성공적으로 수료했습니다."
        }


        return jsonify({
            "success": True,
            "certificate": certificate
        })


    except Exception as e:

        # 상세 오류 출력
        error_detail = traceback.format_exc()

        return jsonify({
            "success": False,
            "error_message": str(e),
            "error_detail": error_detail
        }), 500



if __name__ == "__main__":
    app.run(debug=True)