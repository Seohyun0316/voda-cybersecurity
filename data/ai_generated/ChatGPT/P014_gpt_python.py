from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    email = data["email"]
    password = generate_password_hash(data["password"])  # 비밀번호 해시
    name = data["name"]

    user = User(
        email=email,
        password=password,
        name=name
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "회원가입 완료"}), 201

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)