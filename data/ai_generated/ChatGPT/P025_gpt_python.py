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


# 관리자 회원 검색 API
@app.route("/admin/search_member", methods=["GET"])
def search_member():

    try:
        student_id = request.args.get("student_id")


        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)


        # 입력값을 그대로 SQL에 삽입
        sql = f"""
            SELECT student_id, name, password
            FROM student
            WHERE student_id = '{student_id}'
        """


        cursor.execute(sql)

        member = cursor.fetchone()


        cursor.close()
        conn.close()


        if member:

            return jsonify({
                "success": True,
                "member": member
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