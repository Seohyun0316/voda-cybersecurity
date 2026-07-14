from flask import Flask, request, jsonify
import sqlite3
import logging
from datetime import datetime


app = Flask(__name__)


# 서버 로그 설정
logging.basicConfig(
    filename="survey.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


# DB 생성
def init_db():

    conn = sqlite3.connect("survey.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS survey (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            score INTEGER,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()



# 만족도 조사 저장 API
@app.route("/survey", methods=["POST"])
def save_survey():

    try:
        data = request.get_json()

        name = data["name"]
        email = data["email"]
        score = data["score"]


        conn = sqlite3.connect("survey.db")

        cursor = conn.cursor()


        cursor.execute("""
            INSERT INTO survey
            (name, email, score, created_at)
            VALUES (?, ?, ?, ?)
        """,
        (
            name,
            email,
            score,
            datetime.now()
        ))


        conn.commit()
        conn.close()


        # 서버 로그 기록
        logging.info(
            f"만족도 응답 저장 - 이름:{name}, 이메일:{email}, 점수:{score}"
        )


        return jsonify({
            "success": True,
            "message": "만족도 조사 저장 완료"
        })


    except Exception as e:

        logging.error(
            f"만족도 조사 오류: {str(e)}"
        )

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



# 전체 응답 조회
@app.route("/survey/list", methods=["GET"])
def survey_list():

    conn = sqlite3.connect("survey.db")

    cursor = conn.cursor()


    cursor.execute("""
        SELECT *
        FROM survey
    """)


    result = cursor.fetchall()

    conn.close()


    return jsonify(result)



if __name__ == "__main__":

    init_db()

    app.run(debug=True)