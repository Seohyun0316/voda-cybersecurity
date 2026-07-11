import urllib.request
import json

# 발급받은 자격증명 설정
client_id = "testid123"
client_secret = "testsecret456"

# 검색할 단어 설정 (URL 인코딩 필요)
encText = urllib.parse.quote("네이버 오픈API")

# 검색 카테고리 설정 (예: news, blog, cafearticle, shop 등)
category = "news" 
url = f"https://openapi.naver.com/v1/search/{category}.json?query={encText}"

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id", client_id)
request.add_header("X-Naver-Client-Secret", client_secret)

try:
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    
    if rescode == 200:
        response_body = response.read()
        # 결과를 읽기 편하게 JSON 형식으로 변환하여 출력
        data = json.loads(response_body.decode('utf-8'))
        print(json.dumps(data, indent=4, ensure_ascii=False))
    else:
        print(f"Error Code: {rescode}")
        
except Exception as e:
    print(f"An error occurred: {e}")