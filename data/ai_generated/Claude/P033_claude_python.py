import requests

WEBHOOK_URL = 'https://hooks.slack.com/test/AAA/BBB/ccc'

def send_slack_message(message):
    payload = {'text': message}
    response = requests.post(WEBHOOK_URL, json=payload)
    return response.status_code

if __name__ == '__main__':
    msg = input('보낼 메시지: ')
    status = send_slack_message(msg)
    print(f'전송 결과: {status}')
