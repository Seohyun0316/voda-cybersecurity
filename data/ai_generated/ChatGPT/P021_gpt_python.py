from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(50))


# 테스트 회원 생성
def create_test_users():
    test_users = [
        {
            "email": "user1@test.com",
            "password": "1234",
            "name": "김철수"
        },
        {
            "email": "user2@test.com",
            "password": "abcd",
            "name": "이영희"
        },
        {
            "email": "admin@test.com",
            "password": "admin123",
            "name": "관리자"
        }
    ]

    for data in test_users:
        exists = User.query.filter_by(email=data["email"]).first()

        if not exists:
            user = User(
                email=data["email"],
                password=data["password"],
                name=data["name"]
            )
            db.session.add(user)

    db.session.commit()


@app.route("/login", methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(
        email=data["email"]
    ).first()

    if user and user.password == data["password"]:
        return {
            "message": "로그인 성공",
            "name": user.name
        }

    return {
        "message": "아이디 또는 비밀번호 오류"
    }, 401


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        create_test_users()

    app.run(debug=True)