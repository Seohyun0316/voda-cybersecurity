import requests

SERVICE_KEY = "SVCKEY-TEST-11223344"

url = "https://apis.data.go.kr/서비스명/엔드포인트"

params = {
    "serviceKey": SERVICE_KEY,
    "pageNo": 1,
    "numOfRows": 10
}

response = requests.get(url, params=params)

print(response.status_code)
print(response.text)