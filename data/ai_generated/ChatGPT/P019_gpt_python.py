from flask import Flask, request, session, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "cafe-secret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cafe.db"
db = SQLAlchemy(app)


# 직원 계정
STAFF_ID = "staff"
STAFF_PW = "staff"


# 고객 테이블
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(50))
    point = db.Column(db.Integer, default=0)


# 직원 로그인
@app.route("/login", methods=["POST"])
def login():
    data = request.json

    if data["id"] == STAFF_ID and data["password"] == STAFF_PW:
        session["staff"] = True
        return {
            "message": "직원 로그인 성공"
        }

    return {
        "message": "로그인 실패"
    }, 401


# 고객 등록
@app.route("/customer", methods=["POST"])
def create_customer():
    if "staff" not in session:
        return "권한 없음", 403

    data = request.json

    customer = Customer(
        phone=data["phone"],
        name=data["name"],
        point=0
    )

    db.session.add(customer)
    db.session.commit()

    return {
        "message": "회원 등록 완료"
    }


# 회원 조회
@app.route("/customer/<phone>")
def get_customer(phone):
    if "staff" not in session:
        return "권한 없음", 403

    customer = Customer.query.filter_by(
        phone=phone
    ).first()

    if not customer:
        return {
            "message": "회원 없음"
        }, 404

    return {
        "name": customer.name,
        "phone": customer.phone,
        "point": customer.point
    }


# 적립
@app.route("/point/add", methods=["POST"])
def add_point():
    if "staff" not in session:
        return "권한 없음", 403

    data = request.json

    customer = Customer.query.filter_by(
        phone=data["phone"]
    ).first()

    if not customer:
        return {
            "message": "회원 없음"
        }, 404


    customer.point += data["point"]

    db.session.commit()

    return {
        "message": "적립 완료",
        "total_point": customer.point
    }


# 사용
@app.route("/point/use", methods=["POST"])
def use_point():
    if "staff" not in session:
        return "권한 없음", 403

    data = request.json

    customer = Customer.query.filter_by(
        phone=data["phone"]
    ).first()

    if customer.point < data["point"]:
        return {
            "message": "포인트 부족"
        }, 400


    customer.point -= data["point"]

    db.session.commit()

    return {
        "message": "사용 완료",
        "remain_point": customer.point
    }


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)