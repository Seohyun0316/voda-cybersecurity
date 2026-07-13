import requests

CLIENT_ID = "testid123"
CLIENT_SECRET = "testsecret456"

url = "https://openapi.naver.com/v1/search/news.json"

headers = {
    "X-Naver-Client-Id": CLIENT_ID,
    "X-Naver-Client-Secret": CLIENT_SECRET
}

params = {
    "query": "ÆÄÀÌ½ã",
    "display": 10,
    "start": 1,
    "sort": "sim"
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()

    for item in data["items"]:
        print(item["title"])
        print(item["link"])
        print()
else:
    print("¿À·ù:", response.status_code)
    print(response.text)