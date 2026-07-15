import requests

KAKAO_REST_KEY = 'KAKAOTEST7890'

def search_address(query):
    url = 'https://dapi.kakao.com/v2/local/search/address.json'
    headers = {'Authorization': f'KakaoAK {KAKAO_REST_KEY}'}
    params = {'query': query}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

if __name__ == '__main__':
    address = input('주소 입력: ')
    result = search_address(address)
    for doc in result.get('documents', []):
        print(doc['address_name'], doc['x'], doc['y'])
