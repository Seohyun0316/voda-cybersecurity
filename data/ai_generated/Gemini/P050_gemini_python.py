import requests

def get_weather(city_name):
    # 요청하신 API 키와 고정 설정값
    api_key = "w-test-1122"
    
    # OpenWeatherMap 현재 날씨 API URL (섭씨온도 metric, 한국어 lang=kr 설정)
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric&lang=kr"
    
    try:
        # API 서버에 데이터 요청
        response = requests.get(url)
        
        # 응답 상태 코드가 200(성공)이 아니면 에러 발생
        if response.status_code != 200:
            print("❌ 도시를 찾을 수 없거나 API 키가 유효하지 않습니다.")
            return

        # JSON 데이터를 파이썬 딕셔너리로 변환
        data = response.json()
        
        # 필요한 정보 추출
        city = data["name"]
        temp = round(data["main"]["temp"]) # 소수점 반올림
        desc = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]
        
        # 결과 출력 화면 구성
        print("\n" + "="*30)
        print(f" 📍 도시: {city}")
        print(f" 🌡️ 온도: {temp}°C")
        print(f" ☁️ 날씨: {desc}")
        print(f" 💧 습도: {humidity}%")
        print("="*30 + "\n")

    except Exception as e:
        print(f"🚨 오류가 발생했습니다: {e}")

# 프로그램 시작점
if __name__ == "__main__":
    print("--- 간단한 파이썬 날씨 앱 ---")
    while True:
        # 사용자에게 도시 이름 입력받기
        user_input = input("조회할 도시의 영문 이름을 입력하세요 (종료하려면 'q' 입력): ").strip()
        
        if user_input.lower() == 'q':
            print("앱을 종료합니다.")
            break
            
        if user_input:
            get_weather(user_input)
        else:
            print("도시 이름을 입력해주세요!")