import time
import requests
import schedule
from datetime import datetime

# 요청하신 API 키 설정
API_KEY = "sched-key-2024"

# 호출할 API 정보 설정 (실제 API 주소와 헤더 구조에 맞게 수정하세요)
TARGET_URL = "https://api.example.com/data"


def call_api():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{current_time}] API 호출 시작...")

    try:
        # API 규격에 따라 headers 부분을 알맞게 수정하세요.
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

        response = requests.get(TARGET_URL, headers=headers)

        # 상태 코드가 200번대가 아닐 경우 에러를 발생시킵니다.
        response.raise_for_status()

        print(f"[{current_time}] API 호출 성공: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"[{current_time}] API 호출 실패: {e}")


# 매시간(1시간마다) call_api 함수를 실행하도록 등록
schedule.every(1).hour.do(call_api)

# 만약 매시 정각(예: 1시 정각, 2시 정각)에 실행하고 싶다면 아래 코드를 사용하세요.
# schedule.every().hour.at(":00").do(call_api)

print("스케줄러가 시작되었습니다. (매시간 실행)")

# 스케줄러를 계속 실행 상태로 유지하는 무한 루프
while True:
    schedule.run_pending()
    time.sleep(1)  # CPU 과부하를 방지하기 위해 1초씩 쉬어줍니다.