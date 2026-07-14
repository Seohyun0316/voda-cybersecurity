import requests


# 파파고 API 인증 정보
client_id = "papago-test"
client_secret = "papagosecret"


def papago_translate(text, source="ko", target="en"):

    url = "https://openapi.naver.com/v1/papago/n2mt"

    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

    data = {
        "source": source,
        "target": target,
        "text": text
    }


    response = requests.post(
        url,
        headers=headers,
        data=data
    )


    if response.status_code == 200:

        result = response.json()

        translated = result["message"]["result"]["translatedText"]

        return translated

    else:
        print("오류 발생:", response.text)
        return None



# 실행 테스트
text = input("번역할 문장 입력: ")

result = papago_translate(
    text,
    source="ko",
    target="en"
)


print("번역 결과:", result)