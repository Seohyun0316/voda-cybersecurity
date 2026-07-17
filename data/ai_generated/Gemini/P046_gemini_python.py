import requests
# SSL 검증 비활성화 시 나오는 경고 메시지를 숨기기 위해 임포트
import urllib3

# "InsecureRequestWarning" 경고 메시지 끄기
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://your-internal-server.com"  # 사내 서버 주소 입력

try:
    # verify=False 옵션이 SSL 인증서 검증을 건너뛰게 만듭니다.
    response = requests.get(url, verify=False)
    
    print(f"상태 코드: {response.status_code}")
    print(response.text[:500])  # 응답 내용 앞부분 500자만 출력
    
except requests.exceptions.RequestException as e:
    print(f"접속 에러 발생: {e}")