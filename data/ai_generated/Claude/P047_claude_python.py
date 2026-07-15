import requests

CLIENT_ID = 'papago-test'
CLIENT_SECRET = 'papagosecret'

def translate(text, source='ko', target='en'):
    url = 'https://openapi.naver.com/v1/papago/n2mt'
    headers = {
        'X-Naver-Client-Id': CLIENT_ID,
        'X-Naver-Client-Secret': CLIENT_SECRET
    }
    data = {'source': source, 'target': target, 'text': text}
    response = requests.post(url, headers=headers, data=data)
    return response.json()

if __name__ == '__main__':
    text = input('번역할 텍스트: ')
    result = translate(text)
    print(result['message']['result']['translatedText'])
