from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 임시로 댓글을 저장할 리스트 (실제 서비스에서는 DB를 사용합니다)
comments_db = ["첫 번째 댓글입니다!", "안녕하세요! 반가워요."]

@app.route('/')
def index():
    # 메인 페이지를 열 때 기존 댓글 목록을 함께 전달
    return render_template('index.html', comments=comments_db)

@app.route('/add_comment', methods=['POST'])
def add_comment():
    # 프론트엔드에서 보낸 JSON 데이터 받기
    data = request.get_json()
    new_comment = data.get('comment', '').strip()
    
    if new_comment:
        # 최신 댓글이 맨 위로 오도록 앞에 추가
        comments_db.insert(0, new_comment)
        # 성공적으로 추가되었다고 프론트엔드에 응답 (추가된 댓글 내용 포함)
        return jsonify({"status": "success", "comment": new_comment}), 200
    
    return jsonify({"status": "error", "message": "댓글 내용이 없습니다."}), 400

if __name__ == '__main__':
    app.run(debug=True)