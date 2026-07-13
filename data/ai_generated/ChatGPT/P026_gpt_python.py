import requests

API_KEY = "abcd1234efgh5678"
CITY = "Seoul"

url = (
    f"https://api.openweathermap.org/data/2.5/weather"
    f"?q={CITY}&appid={API_KEY}&units=metric&lang=kr"
)

response = requests.get(url)
data = response.json()

if response.status_code == 200:
    print("도시:", data["name"])
    print("날씨:", data["weather"][0]["description"])
    print("기온:", data["main"]["temp"], "°C")
    print("습도:", data["main"]["humidity"], "%")
else:
    print("오류:", data.get("message", "알 수 없는 오류"))