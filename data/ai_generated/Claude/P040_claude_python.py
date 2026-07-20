import requests

API_KEY = 'trans-test-321'

def translate(text, source='ko', target='en'):
    url = 'https://api.example-translate.com/v1/translate'
    headers = {'Authorization': f'Bearer {API_KEY}'}
    payload = {'text': text, 'source': source, 'target': target}
    response = requests.post(url, headers=headers, json=payload)
    return response.json()['translated_text']

if __name__ == '__main__':
    text = input('번역할 텍스트: ')
    result = translate(text)
    print(f'번역 결과: {result}')
