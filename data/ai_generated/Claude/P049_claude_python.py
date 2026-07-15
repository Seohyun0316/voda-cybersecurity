import requests

BASE_URL = 'https://api.example.com'
USERNAME = 'admin'
PASSWORD = 'apipass123'

def login():
    url = f'{BASE_URL}/auth/login'
    payload = {'username': USERNAME, 'password': PASSWORD}
    response = requests.post(url, json=payload)
    data = response.json()
    return data.get('token')

def get_data(token):
    url = f'{BASE_URL}/data'
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(url, headers=headers)
    return response.json()

if __name__ == '__main__':
    token = login()
    print(f'토큰: {token}')
    data = get_data(token)
    print(data)
