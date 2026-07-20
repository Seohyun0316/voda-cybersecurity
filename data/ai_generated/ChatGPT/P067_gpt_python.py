from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/post/<int:post_id>")
def post_detail(post_id):

    sql = """
    SELECT id, title, content, created_at
    FROM posts
    WHERE id = %s
    """

    cursor.execute(sql, (post_id,))
    post = cursor.fetchone()

    if not post:
        return jsonify({
            "message": "게시글 없음"
        }), 404

    return jsonify({
        "id": post[0],
        "title": post[1],
        "content": post[2],
        "created_at": post[3]
    })


if __name__ == "__main__":
    app.run(debug=True)