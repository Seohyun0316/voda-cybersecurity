import requests

API_KEY = 'fx-demo-5566'

def get_exchange_rate(base='USD', target='KRW'):
    url = f'https://api.exchangerate.host/latest?base={base}&symbols={target}&access_key={API_KEY}'
    response = requests.get(url)
    data = response.json()
    return data

if __name__ == '__main__':
    result = get_exchange_rate()
    print(result)
