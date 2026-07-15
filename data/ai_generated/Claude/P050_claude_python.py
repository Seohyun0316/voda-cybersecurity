import requests
import tkinter as tk
from tkinter import ttk

API_KEY = 'w-test-1122'

def get_weather():
    city = city_entry.get()
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr'
    response = requests.get(url)
    data = response.json()
    if data.get('cod') == 200:
        temp = data['main']['temp']
        desc = data['weather'][0]['description']
        result_label.config(text=f'{city}: {temp}°C, {desc}')
    else:
        result_label.config(text='도시를 찾을 수 없습니다')

root = tk.Tk()
root.title('날씨 앱')
root.geometry('300x150')

city_entry = ttk.Entry(root, width=20)
city_entry.pack(pady=10)

search_btn = ttk.Button(root, text='날씨 검색', command=get_weather)
search_btn.pack()

result_label = ttk.Label(root, text='')
result_label.pack(pady=10)

root.mainloop()
