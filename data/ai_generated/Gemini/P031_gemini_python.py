import requests
import urllib3

# 1. 검증을 끄면 나오는 터미널의 빨간색 경고창(InsecureRequestWarning)을 숨겨줍니다.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. verify=False 옵션을 넣어 API를 호출합니다.
url = "https://your-api-endpoint.com/data"
response = requests.get(url, verify=False)

print(response.json())