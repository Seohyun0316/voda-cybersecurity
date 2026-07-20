from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///event.db"
db = SQLAlchemy(app)


# 응모자 테이블
class Applicant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)


# 이벤트 응모
@app.route("/event/apply", methods=["POST"])
def apply_event():
    data = request.json

    applicant = Applicant(
        name=data["name"],
        phone=data["phone"]
    )

    db.session.add(applicant)
    db.session.commit()

    return jsonify({
        "message": "응모 완료",
        "id": applicant.id
    })


# 응모자 목록
@app.route("/event/list", methods=["GET"])
def event_list():
    applicants = Applicant.query.order_by(
        Applicant.id.desc()
    ).all()

    return jsonify([
        {
            "id": a.id,
            "name": a.name,
            "phone": a.phone
        }
        for a in applicants
    ])


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)