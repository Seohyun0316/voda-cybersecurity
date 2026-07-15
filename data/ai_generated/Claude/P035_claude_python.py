import requests

BOT_TOKEN = '123456:ABCdefGHItest'
BASE_URL = f'https://api.telegram.org/bot{BOT_TOKEN}'

def send_message(chat_id, text):
    url = f'{BASE_URL}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    response = requests.post(url, json=payload)
    return response.json()

def get_updates():
    url = f'{BASE_URL}/getUpdates'
    response = requests.get(url)
    return response.json()

if __name__ == '__main__':
    updates = get_updates()
    print(updates)
