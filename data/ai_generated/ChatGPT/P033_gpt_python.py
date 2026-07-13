import requests

WEBHOOK_URL = "https://hooks.slack.com/test/AAA/BBB/ccc"

message = {
    "text": "안녕하세요! 파이썬에서 보낸 Slack 알림입니다."
}

response = requests.post(WEBHOOK_URL, json=message)

if response.status_code == 200:
    print("메시지 전송 성공!")
else:
    print("전송 실패:", response.status_code)
    print(response.text)