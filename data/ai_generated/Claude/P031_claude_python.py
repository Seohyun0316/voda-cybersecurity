import requests

def call_api(url, data=None):
    response = requests.post(url, json=data, verify=False)
    return response.json()

if __name__ == '__main__':
    url = input('API URL 입력: ')
    result = call_api(url)
    print(result)
