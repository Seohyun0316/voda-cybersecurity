from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime


app = Flask(__name__)


# DB 생성
def init_db():

    conn = sqlite3.connect("hospital.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT,
            phone TEXT,
            birth TEXT,
            department TEXT,
            reservation_date TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()



# 진료 예약 등록 API
@app.route("/reservation", methods=["POST"])
def create_reservation():

    try:

        data = request.get_json()

        patient_name = data["patient_name"]
        phone = data["phone"]
        birth = data["birth"]
        department = data["department"]
        reservation_date = data["reservation_date"]


        conn = sqlite3.connect("hospital.db")

        cursor = conn.cursor()


        cursor.execute("""
            INSERT INTO reservation
            (
                patient_name,
                phone,
                birth,
                department,
                reservation_date,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            patient_name,
            phone,
            birth,
            department,
            reservation_date,
            datetime.now()
        ))


        conn.commit()
        conn.close()


        return jsonify({
            "success": True,
            "message": "진료 예약 완료"
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



# 예약 목록 조회 API
@app.route("/reservation", methods=["GET"])
def get_reservation():

    conn = sqlite3.connect("hospital.db")

    cursor = conn.cursor()


    cursor.execute("""
        SELECT *
        FROM reservation
        ORDER BY id DESC
    """)


    result = cursor.fetchall()

    conn.close()


    return jsonify({
        "reservations": result
    })



if __name__ == "__main__":

    init_db()

    # 디버그 모드 활성화
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )