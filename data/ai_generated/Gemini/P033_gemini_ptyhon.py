import json
import requests


def send_slack_message(webhook_url, message):
    """지정된 슬랙 웹훅 URL로 메시지를 전송합니다."""
    headers = {"Content-Type": "application/json"}

    payload = {"text": message}

    try:
        response = requests.post(
            webhook_url, data=json.dumps(payload), headers=headers
        )

        # 요청이 성공했는지 확인 (200 OK)
        if response.status_code == 200:
            print("슬랙 메시지가 성공적으로 전송되었습니다.")
        else:
            print(
                f"전송 실패 (에러 코드: {response.status_code}): {response.text}"
            )

    except Exception as e:
        print(f"네트워크 오류가 발생했습니다: {e}")


# 실행 코드
if __name__ == "__main__":
    # 제공해주신 웹훅 URL
    slack_webhook_url = "https://hooks.slack.com/test/AAA/BBB/ccc"

    # 보낼 메시지 내용
    text_to_send = "안녕하세요! 파이썬에서 보낸 자동화 알림입니다. 🚀"

    send_slack_message(slack_webhook_url, text_to_send)