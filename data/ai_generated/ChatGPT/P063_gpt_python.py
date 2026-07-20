from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///questions.db"
db = SQLAlchemy(app)


# 질문 테이블
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)


# 질문 등록
@app.route("/question", methods=["POST"])
def create_question():
    data = request.json

    question = Question(
        content=data["content"]
    )

    db.session.add(question)
    db.session.commit()

    return jsonify({
        "message": "질문 등록 완료",
        "id": question.id
    })


# 질문 목록
@app.route("/questions", methods=["GET"])
def question_list():
    questions = Question.query.order_by(
        Question.id.desc()
    ).all()

    return jsonify([
        {
            "id": q.id,
            "content": q.content
        }
        for q in questions
    ])


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)