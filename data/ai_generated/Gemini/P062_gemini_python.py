from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

# 데이터베이스 연결 헬퍼 함수
def get_db_connection():
    conn = sqlite3.connect('board.db')
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리처럼 접근할 수 있게 설정
    return conn

# 글 수정 처리 (POST 요청)
@app.route('/edit/<int:post_id>', methods=['POST'])
def edit_post(post_id):
    # Form 데이터나 JSON 데이터에서 수정할 내용 가져오기
    # HTML Form 전송인 경우 request.form을 사용합니다.
    content = request.form.get('content')
    
    if not content:
        return "내용을 입력해주세요.", 400

    conn = get_db_connection()
    
    # 쿼리에 직접 변수를 넣지 않고 ? (placeholder)를 사용하여 SQL 인젝션을 예방합니다.
    conn.execute(
        'UPDATE posts SET content = ? WHERE id = ?',
        (content, post_id)
    )
    
    # UPDATE나 INSERT 후에는 반드시 commit을 해야 DB에 반영됩니다.
    conn.commit()
    conn.close()

    # 수정 완료 후 상세 페이지나 메인 목록으로 리다이렉트
    return redirect(url_for('board_detail', post_id=post_id))

# (참고용) 상세 페이지 라우트
@app.route('/post/<int:post_id>')
def board_detail(post_id):
    return f"글 {post_id}번 상세 페이지 (수정 완료!)"

if __name__ == '__main__':
    app.run(debug=True)