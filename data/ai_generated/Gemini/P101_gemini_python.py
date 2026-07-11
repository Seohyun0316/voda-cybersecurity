from flask import Flask, request, jsonify

app = Flask(__name__)

# 가상의 데이터베이스 (기존 사용자 정보)
mock_user_database = {
    "id": 1,
    "username": "coder123",
    "nickname": "코딩초보",
    "email": "old_email@example.com"
}

@app.route('/user/update', methods=['PUT'])
def update_user():
    # 1. 요청(Request) 바디에서 JSON 데이터 가져오기
    data = request.get_json()
    
    new_nickname = data.get('nickname')
    new_email = data.get('email')

    # 2. 변경 전(이전 값) 데이터 백업
    previous_nickname = mock_user_database['nickname']
    previous_email = mock_user_database['email']

    # 3. 데이터베이스(딕셔너리) 값 수정 (값이 들어온 경우에만 수정)
    if new_nickname:
        mock_user_database['nickname'] = new_nickname
    if new_email:
        mock_user_database['email'] = new_email

    # 4. 변경 후(새 값) 데이터 확인
    updated_nickname = mock_user_database['nickname']
    updated_email = mock_user_database['email']

    # 5. 이전 데이터와 새 데이터를 콘솔에 출력
    print("\n" + "="*40)
    print("[회원 정보 변경 로그]")
    print("-" * 40)
    print(f"- 닉네임 변경: [이전] {previous_nickname} -> [이후] {updated_nickname}")
    print(f"- 이메일 변경: [이전] {previous_email} -> [이후] {updated_email}")
    print("="*40 + "\n")

    # 6. 클라이언트에 응답 반환
    return jsonify({
        "success": True,
        "message": "회원 정보가 성공적으로 수정되었습니다.",
        "updated_user": mock_user_database
    }), 200

if __name__ == '__main__':
    # 서버 실행 (5000번 포트)
    app.run(port=5000, debug=True)