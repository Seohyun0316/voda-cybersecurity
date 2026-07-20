import requests

DISCORD_WEBHOOK = 'https://discord.com/api/webhooks/test/xyz'

def send_discord(message, username='Bot'):
    payload = {'content': message, 'username': username}
    response = requests.post(DISCORD_WEBHOOK, json=payload)
    print(f'전송 결과: {response.status_code}')

if __name__ == '__main__':
    msg = input('보낼 메시지: ')
    send_discord(msg)
