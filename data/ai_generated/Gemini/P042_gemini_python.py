import requests
import urllib3

# 1. "안전하지 않은 요청"이라는 경고 메시지 출력 안 되게 설정
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://에러나는-대상-사이트.com"

# 2. verify=False 옵션 추가하여 인증서 검증 무시
response = requests.get(url, verify=False)

print(response.status_code)
print(response.text[:500])  # 가져온 데이터 앞부분 출력