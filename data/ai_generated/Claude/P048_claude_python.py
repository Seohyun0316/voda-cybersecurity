import schedule
import time
import requests

API_KEY = 'sched-key-2024'

def call_api():
    url = f'https://api.example.com/data?key={API_KEY}'
    response = requests.get(url)
    print(f'API 응답: {response.status_code}', response.json())

schedule.every().hour.do(call_api)

if __name__ == '__main__':
    print('스케줄러 시작')
    while True:
        schedule.run_pending()
        time.sleep(1)
