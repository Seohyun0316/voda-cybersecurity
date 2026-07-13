import requests

response = requests.get(
    "https://example.com/api",
    verify=False  # 개발/테스트 환경에서만 사용
)

print(response.text)