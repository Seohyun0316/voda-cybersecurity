from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# 임시 데이터베이스 역할을 할 리스트 (서버가 켜져 있는 동안 유지)
reviews_db = [
    {"name": "파이썬조아", "text": "코드가 아주 깔끔하고 잘 작동하네요!", "date": "2026-07-10"}
]

@app.route('/')
def index():
    # 웹 페이지를 열 때 기존 후기 데이터를 함께 넘겨줍니다.
    return render_template('index.html', reviews=reviews_db)

@app.route('/add_review', methods=['POST'])
def add_review():
    # 클라이언트(JavaScript)가 보낸 JSON 데이터를 받습니다.
    data = request.get_json()
    name = data.get('name', '').strip()
    text = data.get('text', '').strip()
    
    if not name or not text:
        return jsonify({"success": False, "message": "이름과 내용을 모두 입력해주세요."}), 400
    
    # 새 후기 객체 생성
    new_review = {
        "name": name,
        "text": text,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    # 최신 후기가 맨 위에 오도록 리스트의 가장 앞에 추가
    reviews_db.insert(0, new_review)
    
    # 성공 메시지와 함께 저장된 후기 데이터를 다시 반환
    return jsonify({"success": True, "review": new_review})

if __name__ == '__main__':
    # 서버 실행 (기본 포트: 5000)
    app.run(debug=True)