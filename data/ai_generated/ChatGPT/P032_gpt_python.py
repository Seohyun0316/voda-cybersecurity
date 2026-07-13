import requests

REST_API_KEY = "KAKAOTEST7890"

url = "https://dapi.kakao.com/v2/local/search/address.json"

headers = {
    "Authorization": f"KakaoAK {REST_API_KEY}"
}

params = {
    "query": "경기도 성남시 수정구"
}

response = requests.get(url, headers=headers, params=params)

if response.status_code == 200:
    data = response.json()

    if data["documents"]:
        result = data["documents"][0]
        print("주소:", result["address"]["address_name"])
        print("경도(X):", result["address"]["x"])
        print("위도(Y):", result["address"]["y"])
    else:
        print("검색 결과가 없습니다.")
else:
    print("오류:", response.status_code)
    print(response.text)