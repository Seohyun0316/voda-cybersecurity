import requests

# 1. URL 및 서비스키 설정
# (실제 사용하실 API의 End Point URL을 입력하세요)
url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst' 
service_key = 'SVCKEY-TEST-11223344'

# 2. 요청 파라미터 설정 (API 명세서에 맞게 수정 필요)
params = {
    'serviceKey' : service_key,
    'pageNo' : '1',
    'numOfRows' : '10',
    'dataType' : 'JSON',  # 요청 데이터 타입 (JSON 또는 XML)
    'base_date' : '20260710',
    'base_time' : '0600',
    'nx' : '55',
    'ny' : '127'
}

try:
    # 3. API 호출
    response = requests.get(url, params=params)
    
    # 4. 응답 데이터 확인
    if response.status_code == 200:
        print("API 호출 성공!")
        
        # JSON 응답인 경우
        try:
            json_data = response.json()
            print(json_data)
        # XML 응답인 경우 (또는 서비스키 에러로 XML이 반환된 경우)
        except ValueError:
            print(response.text)
            
    else:
        print(f"API 호출 실패 (상태코드: {response.status_code})")

except Exception as e:
    print(f"에러 발생: {e}")