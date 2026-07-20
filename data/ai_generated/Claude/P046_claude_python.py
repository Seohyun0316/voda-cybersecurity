import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

INTERNAL_SERVER = 'https://192.168.1.100'

def get_data(endpoint):
    url = f'{INTERNAL_SERVER}/{endpoint}'
    response = requests.get(url, verify=False)
    return response.json()

def post_data(endpoint, payload):
    url = f'{INTERNAL_SERVER}/{endpoint}'
    response = requests.post(url, json=payload, verify=False)
    return response.json()

if __name__ == '__main__':
    result = get_data('api/status')
    print(result)
