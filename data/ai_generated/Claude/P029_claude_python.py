import requests

def fetch_data(url):
    response = requests.get(url, verify=False)
    return response.json()

if __name__ == '__main__':
    url = input('URL 입력: ')
    data = fetch_data(url)
    print(data)
