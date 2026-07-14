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


# 검색어 저장 API
@app.route("/search", methods=["POST"])
def save_search():

    try:
        data = request.get_json()

        keyword = data["keyword"]


        conn = get_connection()
        cursor = conn.cursor()


        # 검색어 그대로 저장
        sql = f"""
            INSERT INTO search_history(keyword)
            VALUES('{keyword}')
        """


        cursor.execute(sql)
        conn.commit()


        cursor.close()
        conn.close()


        return jsonify({
            "success": True,
            "message": "검색어 저장 완료"
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



# 인기 검색어 조회 API
@app.route("/popular", methods=["GET"])
def popular_keyword():

    try:

        conn = get_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)


        sql = """
            SELECT 
                keyword,
                COUNT(*) AS count
            FROM search_history
            GROUP BY keyword
            ORDER BY count DESC
            LIMIT 10
        """


        cursor.execute(sql)

        result = cursor.fetchall()


        cursor.close()
        conn.close()


        return jsonify({
            "success": True,
            "popular_keywords": result
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



if __name__ == "__main__":
    app.run(debug=True)