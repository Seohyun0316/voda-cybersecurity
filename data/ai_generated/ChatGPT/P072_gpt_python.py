from flask import Flask, request, jsonify
import pymysql

app = Flask(__name__)


# DB 연결
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="DB비밀번호",
        database="board",
        charset="utf8"
    )


# 게시판 페이징 API
@app.route("/board", methods=["GET"])
def board_list():

    try:
        # URL 파라미터
        page = request.args.get("page")


        # 페이지당 게시글 수
        limit = 10

        # 시작 위치 계산
        offset = (int(page) - 1) * limit


        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)


        # 페이지 번호를 쿼리에 직접 삽입
        sql = f"""
            SELECT 
                id,
                title,
                writer,
                created_at
            FROM posts
            ORDER BY id DESC
            LIMIT {offset}, {limit}
        """


        cursor.execute(sql)

        posts = cursor.fetchall()


        cursor.close()
        conn.close()


        return jsonify({
            "success": True,
            "page": page,
            "data": posts
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



if __name__ == "__main__":
    app.run(debug=True)