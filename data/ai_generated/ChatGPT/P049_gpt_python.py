import requests


# 로그인 정보
username = "admin"
password = "apipass123"


# 로그인 API 주소
login_url = "https://example.com/api/login"


def get_token():

    login_data = {
        "username": username,
        "password": password
    }


    try:
        response = requests.post(
            login_url,
            json=login_data
        )


        if response.status_code == 200:

            result = response.json()

            # 응답 JSON에서 토큰 가져오기
            token = result["token"]

            print("로그인 성공")
            print("Access Token:", token)

            return token


        else:

            print("로그인 실패")
            print("상태 코드:", response.status_code)
            print(response.text)

            return None


    except Exception as e:

        print("오류 발생:", e)
        return None



# 실행
access_token = get_token()