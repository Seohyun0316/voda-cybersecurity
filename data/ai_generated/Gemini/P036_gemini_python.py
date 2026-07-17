import requests
# SSL 검증 관련 경고 메시지가 콘솔에 가득 차는 것을 방지하기 위해 추가
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://your-company-api.com/endpoint"

# verify=False 설정
response = requests.get(url, verify=False)

print(response.status_code)