import requests

def search_address(address, rest_api_key):
    # 카카오 로컬 API 주소 검색 URL
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    
    # 헤더에 REST API 키 추가 (Authorization: KakaoAK {REST_API_KEY})
    headers = {
        "Authorization": f"KakaoAK {rest_api_key}"
    }
    
    # 검색할 주소를 파라미터로 전달
    params = {
        "query": address
    }
    
    try:
        # API 요청 보내기
        response = requests.get(url, headers=headers, params=params)
        
        # HTTP 상태 코드가 200(성공)인지 확인
        if response.status_code == 200:
            data = response.json()
            
            # 검색 결과가 존재하는지 확인
            if data['documents']:
                print(f"=== '{address}' 검색 결과 ===")
                for doc in data['documents']:
                    address_name = doc['address_name']
                    lon = doc['x']  # 경도 (Longitude)
                    lat = doc['y']  # 위도 (Latitude)
                    
                    print(f"정식 주소: {address_name}")
                    print(f"위도(Lat): {lat}")
                    print(f"경도(Lon): {lon}")
                    print("-" * 30)
            else:
                print("검색 결과가 없습니다.")
        else:
            print(f"API 요청 실패 (에러 코드: {response.status_code})")
            print(response.text)
            
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")

# 실행 변수 설정
REST_KEY = "KAKAOTEST7890"
TARGET_ADDRESS = "판교역로 166"

# 함수 호출
search_address(TARGET_ADDRESS, REST_KEY)