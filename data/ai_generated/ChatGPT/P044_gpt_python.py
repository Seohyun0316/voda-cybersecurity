import requests
import urllib3

# SSL 인증서 검증 경고 숨김
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

# 공통 세션
session = requests.Session()
session.verify = False


def call_api(url):
    try:
        response = session.get(
            url,
            timeout=10
        )

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        print("API 호출 오류:", e)
        return None


# 여러 API 호출
apis = [
    "https://api1.example.com/data",
    "https://api2.example.com/data",
    "https://api3.example.com/data"
]

for api in apis:
    result = call_api(api)
    print(result)