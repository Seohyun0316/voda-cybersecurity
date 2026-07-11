import requests

def get_weather(city_name, api_key):
    # OpenWeather Current Weather API URL
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric&lang=kr"
    
    try:
        response = requests.get(url)
        # HTTP 에러가 발생했을 경우 예외 처리
        response.raise_for_status()
        
        # JSON 데이터 파싱
        data = response.json()
        
        # 필요한 정보 추출
        city = data['name']
        weather_desc = data['weather'][0]['description']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        
        print(f"=== {city}의 현재 날씨 ===")
        print(f"날씨 상태: {weather_desc}")
        print(f"현재 기온: {temp}°C")
        print(f"체감 온도: {feels_like}°C")
        print(f"현재 습도: {humidity}%")
        
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP 에러 발생: {http_err}")
    except Exception as err:
        print(f"기타 에러 발생: {err}")

# 제공해주신 API 키 적용
API_KEY = "abcd1234efgh5678"
CITY = "Seoul"  # 원하는 도시 이름을 영문으로 입력하세요 (예: Busan, Jeju 등)

get_weather(CITY, API_KEY)