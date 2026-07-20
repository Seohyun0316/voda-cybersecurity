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


@app.route("/signup", methods=["POST"])
def signup():
    data = request.json

    user = User(
        email=data["email"],
        password=data["password"],  # 그대로 저장
        name=data["name"]
    )

    db.session.add(user)
    db.session.commit()

    return {
        "message": "회원가입 완료"
    }


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)