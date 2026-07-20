import requests
import urllib3

# SSL 인증서 경고 숨기기
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

url = "https://internal-server.example.com/api"

response = requests.get(
    url,
    verify=False,
    timeout=10
)

print(response.status_code)
print(response.text)