import requests

IMP_ID = 'imp_test_001'
PAY_KEY = 'paykey-demo-789'
API_BASE = 'https://api.iamport.kr'

def get_token():
    resp = requests.post(f'{API_BASE}/users/getToken', json={
        'imp_key': IMP_ID,
        'imp_secret': PAY_KEY
    })
    return resp.json()['response']['access_token']

def verify_payment(imp_uid):
    token = get_token()
    resp = requests.get(
        f'{API_BASE}/payments/{imp_uid}',
        headers={'Authorization': token}
    )
    return resp.json()['response']

if __name__ == '__main__':
    imp_uid = input('imp_uid 입력: ')
    result = verify_payment(imp_uid)
    print(result)
