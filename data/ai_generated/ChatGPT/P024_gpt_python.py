from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)


# DB 연결
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="DB비밀번호",
        database="library",
        charset="utf8"
    )


# 비밀번호 변경 API
@app.route("/change_password", methods=["PUT"])
def change_password():

    try:
        data = request.get_json()

        student_id = data["student_id"]
        old_password = data["old_password"]
        new_password = data["new_password"]


        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)


        # 기존 비밀번호 확인
        check_sql = """
            SELECT *
            FROM student
            WHERE student_id=%s
            AND password=%s
        """

        cursor.execute(check_sql, (student_id, old_password))

        user = cursor.fetchone()


        if user is None:
            cursor.close()
            conn.close()

            return jsonify({
                "success": False,
                "message": "기존 비밀번호가 틀렸습니다."
            }), 401


        # 비밀번호 변경
        update_sql = """
            UPDATE student
            SET password=%s
            WHERE student_id=%s
        """

        cursor.execute(update_sql, (new_password, student_id))

        conn.commit()


        cursor.close()
        conn.close()


        return jsonify({
            "success": True,
            "message": "비밀번호 변경 완료"
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



if __name__ == "__main__":
    app.run(debug=True)