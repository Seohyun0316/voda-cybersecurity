from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///guestbook.db"
db = SQLAlchemy(app)


class Guestbook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)


# 방명록 작성
@app.route("/guestbook", methods=["POST"])
def write_guestbook():
    data = request.json

    item = Guestbook(
        message=data["message"]
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({
        "message": "등록 완료"
    })


# 관리자 페이지 - 전체 목록
@app.route("/admin/guestbook")
def admin_guestbook():
    messages = Guestbook.query.order_by(
        Guestbook.id.desc()
    ).all()

    html = """
    <h1>방명록 관리</h1>

    {% for item in messages %}
        <div style="border-bottom:1px solid #ddd; padding:10px;">
            {{ item.message }}
        </div>
    {% endfor %}
    """

    return render_template_string(
        html,
        messages=messages
    )


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)