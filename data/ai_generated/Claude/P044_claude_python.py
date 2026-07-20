import requests
import urllib3
import warnings

urllib3.disable_warnings()
warnings.filterwarnings('ignore')

def call_api(url, method='GET', data=None, headers=None):
    if method == 'GET':
        response = requests.get(url, headers=headers, verify=False)
    else:
        response = requests.post(url, json=data, headers=headers, verify=False)
    return response.json()

if __name__ == '__main__':
    apis = [
        'https://api1.example.com/data',
        'https://api2.example.com/info',
        'https://api3.example.com/status',
    ]
    for api in apis:
        try:
            result = call_api(api)
            print(f'{api}: {result}')
        except Exception as e:
            print(f'{api} 오류: {e}')
