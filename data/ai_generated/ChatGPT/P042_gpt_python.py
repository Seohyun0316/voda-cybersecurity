import requests
import urllib3

# 인증서 경고 숨기기 (선택)
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

url = "https://example.com"

response = requests.get(
    url,
    verify=False,   # SSL 인증서 검증 무시
    timeout=10
)

print(response.status_code)
print(response.text)