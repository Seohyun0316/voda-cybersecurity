import requests
import urllib3

# 1. SSL 경고 메시지(InsecureRequestWarning) 전부 숨기기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. API 호출 테스트 (verify=False 필수)
urls = [
    "https://expired.badssl.com/",  # 만료된 SSL 예시
    "https://self-signed.badssl.com/"  # 사설 SSL 예시
]

for url in urls:
    try:
        # verify=False로 지정해 에러를 방지합니다.
        response = requests.get(url, verify=False)
        print(f"성공: {url} (상태 코드: {response.status_code})")
    except Exception as e:
        print(f"실패: {url} (에러 이유: {e})")