import requests


# OpenWeather API Key
API_KEY = "w-test-1122"


def get_weather(city):

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "kr"
    }


    response = requests.get(
        url,
        params=params
    )


    if response.status_code == 200:

        data = response.json()


        weather = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]


        print("\n===== 날씨 정보 =====")
        print("도시 :", city)
        print("날씨 :", weather)
        print("온도 :", temp, "℃")
        print("습도 :", humidity, "%")


    else:

        print("날씨 정보를 가져오지 못했습니다.")
        print("오류 코드:", response.status_code)
        print(response.text)



# 실행 부분
if __name__ == "__main__":

    city = input("도시 이름 입력: ")

    get_weather(city)