import requests

SERVICE_KEY = 'SVCKEY-TEST-11223344'

def get_public_data(endpoint, params=None):
    if params is None:
        params = {}
    params['serviceKey'] = SERVICE_KEY
    response = requests.get(endpoint, params=params)
    return response.json()

if __name__ == '__main__':
    url = 'https://api.example.go.kr/data'
    data = get_public_data(url, {'numOfRows': 10, 'pageNo': 1})
    print(data)
