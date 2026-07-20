from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///board.db"
db = SQLAlchemy(app)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)


@app.route("/post/update", methods=["POST"])
def update_post():
    data = request.json

    post_id = data["id"]
    new_content = data["content"]

    post = Post.query.filter_by(id=post_id).first()

    if not post:
        return jsonify({"message": "글 없음"}), 404

    post.content = new_content

    db.session.commit()

    return jsonify({
        "message": "수정 완료"
    })


if __name__ == "__main__":
    app.run(debug=True)