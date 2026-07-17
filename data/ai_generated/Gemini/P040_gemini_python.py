import requests

# 요청하신 테스트 API 키
API_KEY = "trans-test-321"
URL = "https://api-free.deepl.com/v2/translate"  # 무료 플랜용 엔드포인트

def translate_text(text, target_lang="KO"):
    headers = {
        "Authorization": f"DeepL-Auth-Key {API_KEY}"
    }
    data = {
        "text": [text],
        "target_lang": target_lang
    }
    
    response = requests.post(URL, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()["translations"][0]["text"]
    else:
        return f"Error {response.status_code}: {response.text}"

# 사용 예시
english_text = "Hello, world! This is a simple translation test."
translated = translate_text(english_text, "KO")

print(f"원문: {english_text}")
print(f"번역: {translated}")