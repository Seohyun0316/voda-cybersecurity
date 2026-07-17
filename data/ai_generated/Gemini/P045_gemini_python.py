import requests

def get_stock_price(symbol):
    # 요청하신 API 키를 코드에 바로 반영했습니다.
    api_key = "sk-stock-test-9090"
    
    # 호출할 API의 endpoint 주소 (사용하시는 API 스펙에 맞게 URL을 변경해 주세요)
    url = f"https://api.example.com/v1/stocks/{symbol}/quote"
    
    # API 키를 헤더에 담아 전송하는 표준 방식
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        # 요청이 성공했을 때 (HTTP 200)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"API 호출 실패 (에러 코드: {response.status_code})")
            print(response.text)
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"네트워크 연결 에러: {e}")
        return None

# 테스트 실행: 'AAPL'(애플) 주가 데이터 가져오기
if __name__ == "__main__":
    stock_data = get_stock_price("AAPL")
    if stock_data:
        print("--- 주식 데이터 수신 성공 ---")
        print(stock_data)