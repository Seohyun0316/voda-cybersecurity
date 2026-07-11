import requests
import urllib3

# 1. SSL 인증서가 유효하지 않을 때 뜨는 경고 메시지(InsecureRequestWarning) 안 나오게 하기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. 데이터를 가져올 외부 서버 주소
url = "https://외부서버-주소.com/api/data"

try:
    # 3. verify=False 옵션을 주어 SSL 인증서 검증을 무시합니다.
    response = requests.get(url, verify=False)
    
    # 응답 상태 코드 확인 (200이면 성공)
    if response.status_code == 200:
        print("데이터 가져오기 성공!")
        print(response.json())  # JSON 데이터인 경우 데이터 출력
    else:
        print(f"서버 응답 에러 코드: {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"요청 중 에러가 발생했습니다: {e}")