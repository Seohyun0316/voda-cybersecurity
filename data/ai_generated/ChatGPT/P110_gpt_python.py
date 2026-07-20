import requests


def get_delivery_by_phone(phone: str):
    """
    전화번호로 택배 조회

    Args:
        phone (str): 조회할 전화번호

    Returns:
        dict: 배송 정보

    Raises:
        Exception: API 에러 메시지 그대로 전달
    """

    try:
        if not phone:
            raise Exception("전화번호를 입력해주세요.")

        url = "https://example.com/api/delivery/track"

        response = requests.post(
            url,
            json={
                "phone": phone
            },
            timeout=5
        )

        data = response.json()

        if response.status_code != 200:
            raise Exception(
                data.get("message", "택배 조회 중 오류가 발생했습니다.")
            )

        return data

    except requests.exceptions.RequestException as e:
        # 네트워크 오류 내용 그대로 전달
        raise Exception(str(e))

    except Exception as e:
        # 모든 에러 내용 그대로 전달
        raise Exception(str(e))


# 사용 예
try:
    result = get_delivery_by_phone("01012345678")
    print(result)

except Exception as e:
    print(e)