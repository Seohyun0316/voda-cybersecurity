import requests

# 제공해주신 디스코드 웹훅 URL
WEBHOOK_URL = "https://discord.com/api/webhooks/test/xyz"

# 전송할 데이터 구성
data = {
    "content": "안녕하세요! 디스코드 웹훅으로 보내는 테스트 메시지입니다. 🚀",
    "username": "알림 봇",  # 웹훅 프로필 이름을 임시로 변경할 수 있습니다 (생략 가능)
}

try:
    # POST 요청 전송
    response = requests.post(WEBHOOK_URL, json=data)
    
    # HTTP 상태 코드가 200~299 범위가 아니면 에러 발생
    response.raise_for_status()
    print("메시지가 성공적으로 전송되었습니다!")
except requests.exceptions.RequestException as e:
    print(f"메시지 전송 실패: {e}")