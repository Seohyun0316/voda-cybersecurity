import requests

def get_exchange_rate(api_key, base_currency="USD", target_currency="KRW"):
    # ExchangeRate-API 서비스 URL 구조에 키와 기준 통화 적용
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"
    
    try:
        response = requests.get(url)
        # 요청이 성공했는지 확인 (200 OK가 아니면 예외 발생)
        response.raise_for_status() 
        
        data = response.json()
        
        if data.get("result") == "success":
            # 대상 통화의 환율 가져오기
            rate = data["conversion_rates"].get(target_currency)
            if rate:
                print(f"--- 환율 조회 성공 ---")
                print(f"기준 통화: {base_currency}")
                print(f"대상 통화: {target_currency}")
                print(f"현재 환율: 1 {base_currency} = {rate:,} {target_currency}")
                return rate
            else:
                print(f"오류: 지원하지 않거나 찾을 수 없는 통화 코드({target_currency})입니다.")
        else:
            print(f"API 오류: {data.get('error-type', '알 수 없는 오류')}")
            
    except requests.exceptions.RequestException as e:
        print(f"네트워크 또는 HTTP 요청 오류 발생: {e}")
    except Exception as e:
        print(f"오류 발생: {e}")

# 1. 발급받으신 API 키 설정
API_KEY = "fx-demo-5566"

# 2. 함수 호출 (USD -> KRW 환율 조회)
get_exchange_rate(API_KEY, "USD", "KRW")