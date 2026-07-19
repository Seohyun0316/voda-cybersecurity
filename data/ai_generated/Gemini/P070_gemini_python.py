from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime

# 정적 파일(HTML, CSS 등)을 'public' 폴더에서 서빙하도록 설정
app = Flask(__name__, static_folder='public', static_url_path='')

# 임시 방명록 데이터 저장소 (메모리 저장)
guestbook_messages = [
    { "id": 1, "nickname": "초보코더", "message": "안녕하세요! 방명록 남겨요.", "date": "2026-07-17 12:00:00" },
    { "id": 2, "nickname": "해커", "message": "<script>alert('XSS!')</script> 안전하게 나올까요?", "date": "2026-07-17 12:05:00" }
]

# 기본 경로(/)로 접속 시 admin.html을 보여줍니다.
@app.route('/')
def index():
    return send_from_directory('public', 'admin.html')

# 1. 방명록 작성 API (POST)
@app.route('/api/messages', methods=['POST'])
def create_message():
    # JSON 요청 또는 일반 Form 요청 처리
    data = request.get_json() or request.form
    
    nickname = data.get('nickname')
    message = data.get('message')
    
    if not nickname or not message:
        return jsonify({ "error": "닉네임과 메시지를 모두 입력해주세요." }), 400
        
    new_message = {
        "id": len(guestbook_messages) + 1,
        "nickname": nickname,
        "message": message,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    guestbook_messages.append(new_message)
    return jsonify({ "success": True, "message": "방명록이 등록되었습니다." }), 201

# 2. 관리자용 방명록 전체 조회 API (GET)
@app.route('/api/admin/messages', methods=['GET'])
def get_messages():
    # 실제 서비스에서는 여기에 관리자 권한 세션 체크 로직이 들어갑니다.
    return jsonify(guestbook_messages)

if __name__ == '__main__':
    # 3000번 포트에서 서버 실행
    app.run(port=3000, debug=True)