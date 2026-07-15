import requests

API_KEY = 'abcd1234efgh5678'

def get_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr'
    response = requests.get(url)
    data = response.json()
    return data

if __name__ == '__main__':
    city = input('도시 이름 입력: ')
    weather = get_weather(city)
    print(weather)
