import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('board.db')

@app.route('/post/<post_id>')
def get_post(post_id):
    conn = get_db()
    query = "SELECT * FROM posts WHERE id = " + post_id
    post = conn.execute(query).fetchone()
    conn.close()
    if post:
        return jsonify({'post': post})
    return jsonify({'message': '게시글 없음'}), 404

if __name__ == '__main__':
    app.run(debug=True)
