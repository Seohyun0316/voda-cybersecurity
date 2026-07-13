import json
import requests

# 발급받은 API 키 설정
CLIENT_ID = "papago-test"
CLIENT_SECRET = "papagosecret"


def translate_text(text, source="ko", target="en"):
    """텍스트를 번역하는 함수

    :param text: 번역할 전체 문장
    :param source: 원본 언어 코드 (기본값: 한국어 'ko')
    :param target: 목적 언어 코드 (기본값: 영어 'en')
    """
    url = "https://openapi.naver.com/v1/papago/n2mt"

    # HTTP Header 설정
    headers = {
        "X-Naver-Client-Id": CLIENT_ID,
        "X-Naver-Client-Secret": CLIENT_SECRET,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # 전송할 데이터 (텍스트, 출발어, 목적어)
    data = {"text": text, "source": source, "target": target}

    try:
        # POST 요청 보내기
        response = requests.post(url, headers=headers, data=data)

        # 응답 코드가 200(성공)인 경우
        if response.status_code == 200:
            response_json = response.json()
            # JSON 구조에서 번역된 텍스트만 추출
            translated_text = response_json["message"]["result"][
                "translatedText"
            ]
            return translated_text
        else:
            print(f"Error Code: {response.status_code}")
            print(f"Error Message: {response.text}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# --- 사용 예시 ---
if __name__ == "__main__":
    original_text = "안녕하세요. 오늘 날씨가 참 좋네요. 파파고 API를 테스트 중입니다."

    print(f"원문: {original_text}")

    # 한국어(ko) -> 영어(en) 번역
    english_result = translate_text(original_text, source="ko", target="en")
    print(f"영어 번역: {english_result}")

    print("-" * 30)

    # 한국어(ko) -> 일본어(ja) 번역
    japanese_result = translate_text(original_text, source="ko", target="ja")
    print(f"일본어 번역: {japanese_result}")