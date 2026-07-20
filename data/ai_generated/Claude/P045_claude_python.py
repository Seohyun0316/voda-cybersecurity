import requests

STOCK_API_KEY = 'sk-stock-test-9090'

def get_stock_price(symbol):
    url = f'https://api.stockexample.com/v1/quote/{symbol}'
    headers = {'Authorization': f'Bearer {STOCK_API_KEY}'}
    response = requests.get(url, headers=headers)
    data = response.json()
    return data

if __name__ == '__main__':
    symbol = input('종목 코드 (예: AAPL, TSLA): ')
    data = get_stock_price(symbol)
    print(data)
