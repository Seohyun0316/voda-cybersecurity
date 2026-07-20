from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

IMP_STORE_ID = os.environ.get("IMP_STORE_ID")
IMP_API_KEY = os.environ.get("IMP_API_KEY")


# 결제 요청 생성
@app.route("/payment/request", methods=["POST"])
def payment_request():
    data = request.json

    payment = {
        "merchant_uid": data["order_id"],
        "amount": data["amount"],
        "name": data["product_name"]
    }

    # 프론트 결제창에서 사용할 정보 반환
    return jsonify({
        "store_id": IMP_STORE_ID,
        "payment": payment
    })


# 결제 검증
@app.route("/payment/verify", methods=["POST"])
def payment_verify():
    data = request.json

    imp_uid = data["imp_uid"]

    # 결제 검증용 토큰 발급
    token_response = requests.post(
        "https://api.iamport.kr/users/getToken",
        json={
            "imp_key": IMP_API_KEY,
            "imp_secret": os.environ.get("IMP_SECRET")
        }
    )

    token = token_response.json()["response"]["access_token"]


    # 결제 정보 조회
    payment_response = requests.get(
        f"https://api.iamport.kr/payments/{imp_uid}",
        headers={
            "Authorization": token
        }
    )

    payment_data = payment_response.json()


    if payment_data["response"]["status"] == "paid":
        return {
            "message": "결제 성공",
            "amount": payment_data["response"]["amount"]
        }

    return {
        "message": "결제 실패"
    }, 400


if __name__ == "__main__":
    app.run(debug=True)