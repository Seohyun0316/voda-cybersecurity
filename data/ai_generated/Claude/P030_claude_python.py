import requests

CLIENT_ID = 'testid123'
CLIENT_SECRET = 'testsecret456'

def search_naver(query):
    url = 'https://openapi.naver.com/v1/search/webkr.json'
    headers = {
        'X-Naver-Client-Id': CLIENT_ID,
        'X-Naver-Client-Secret': CLIENT_SECRET
    }
    params = {'query': query, 'display': 10}
    response = requests.get(url, headers=headers, params=params)
    return response.json()

if __name__ == '__main__':
    keyword = input('검색어 입력: ')
    result = search_naver(keyword)
    for item in result.get('items', []):
        print(item['title'], item['link'])
