import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_BASE = 'https://internal.company.com/api'

def call_api(endpoint, data=None):
    url = f'{API_BASE}/{endpoint}'
    response = requests.post(url, json=data, verify=False)
    return response.json()

if __name__ == '__main__':
    result = call_api('users/list')
    print(result)
