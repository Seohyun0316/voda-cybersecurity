from flask import Flask, jsonify, abort
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('board.db')
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형태로 받기 위함
    return conn

# 게시글 조회 API (예: /post/12)
@app.route('/post/<int:post_id>', methods=['GET'])
def get_post(post_id):
    conn = get_db_connection()
    
    # 안전한 방식: 플레이스홀더(?)를 사용하고 파라미터는 튜플로 전달
    query = "SELECT * FROM posts WHERE id = ?"
    post = conn.execute(query, (post_id,)).fetchone()
    
    conn.close()

    if post is None:
        abort(404, description="게시글을 찾을 수 없습니다.")

    # 결과를 딕셔너리로 변환하여 반환
    return jsonify(dict(post))

if __name__ == '__main__':
    app.run(debug=True)