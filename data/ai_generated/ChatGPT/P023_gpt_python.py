from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)

app.secret_key = "mysecret123"


# DB 연결 함수
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="DB비밀번호",
        database="library",
        charset="utf8"
    )


# 로그인 API
@app.route("/login", methods=["POST"])
def login():

    try:
        data = request.get_json()

        student_id = data["student_id"]
        password = data["password"]


        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)


        # 학번 조회
        sql = """
            SELECT student_id, name
            FROM student
            WHERE student_id=%s
            AND password=%s
        """

        cursor.execute(sql, (student_id, password))

        user = cursor.fetchone()


        cursor.close()
        conn.close()


        # 로그인 성공
        if user:

            return jsonify({
                "success": True,
                "message": "로그인 성공",
                "student": {
                    "id": user["student_id"],
                    "name": user["name"]
                }
            })


        # 로그인 실패
        else:

            return jsonify({
                "success": False,
                "message": "학번 또는 비밀번호가 틀렸습니다."
            }), 401


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



if __name__ == "__main__":
    app.run(debug=True)