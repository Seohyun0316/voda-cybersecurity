import os
import requests


WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]


def send_discord_message(message):
    data = {
        "content": message
    }

    response = requests.post(
        WEBHOOK_URL,
        json=data
    )

    if response.status_code == 204:
        print("전송 성공")
    else:
        print("전송 실패:", response.status_code, response.text)


send_discord_message(
    "테스트 메시지입니다."
)