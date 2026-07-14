import requests
from apscheduler.schedulers.blocking import BlockingScheduler


# API Key
API_KEY = "sched-key-2024"


# 호출할 API 함수
def call_api():

    url = "https://example.com/api/data"

    headers = {
        "Authorization": API_KEY
    }

    try:
        response = requests.get(
            url,
            headers=headers
        )

        print("API 호출 완료")
        print("상태 코드:", response.status_code)
        print("응답:", response.text)


    except Exception as e:
        print("API 호출 오류:", e)



# 스케줄러 생성
scheduler = BlockingScheduler()


# 매시간 실행
scheduler.add_job(
    call_api,
    trigger="interval",
    hours=1
)


print("매시간 API 호출 스케줄러 실행 중...")


try:
    scheduler.start()

except KeyboardInterrupt:
    print("스케줄러 종료")