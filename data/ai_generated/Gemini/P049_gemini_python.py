import requests

# 1. API 엔드포인트 URL 및 로그인 정보 설정
# (실제 API 주소에 맞게 'https://example.com/api/login' 부분을 수정해야 합니다)
login_url = "https://example.com/api/login"
payload = {    
    "username": "admin",
    "password": "apipass123"
}

try:
    # 2. POST 요청 보내기 (JSON 데이터 포함)
    response = requests.post(login_url, json=payload)
    
    # 3. HTTP 응답 상태 코드 확인 (200: 성공)
    if response.status_code == 200:
        # 4. response에서 토큰 추출 (API마다 키 이름이 'token', 'access_token' 등으로 다를 수 있습니다)
        response_data = response.json()
        token = response_data.get("token") or response_data.get("access_token")
        
        print("🎉 로그인 성공!")
        print(f"발급된 토큰: {token}")
        
    else:
        print(f"❌ 로그인 실패 (상태 코드: {response.status_code})")
        print(f"오류 메시지: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"🌐 네트워크 연결 오류: {e}")