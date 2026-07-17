from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

# 1. 요청 데이터를 검증할 Pydantic 모델 정의
class PaymentData(BaseModel):
    imp_uid: str
    merchant_uid: str

# 가맹점 API 키 설정
PORTONE_API_KEY = "paykey-demo-789"
PORTONE_API_SECRET = "your_api_secret_here"  # 포트원 콘솔에서 발급받은 Secret 입력

@app.post("/payment/complete")
def verify_payment(data: PaymentData):
    try:
        # 1. 포트원 REST API용 액세스 토큰(Access Token) 발급 받기
        token_response = requests.post(
            "https://api.iamport.kr/users/getToken",
            json={
                "imp_key": PORTONE_API_KEY,
                "imp_secret": PORTONE_API_SECRET
            }
        )
        token_data = token_response.json()
        
        if token_response.status_code != 200 or "response" not in token_data:
            raise HTTPException(status_code=400, detail="토큰 발급에 실패했습니다.")
            
        access_token = token_data["response"]["access_token"]

        # 2. 발급받은 토큰으로 포트원 서버에서 실제 결제 내역 가져오기
        payment_response = requests.get(
            f"https://api.iamport.kr/payments/{data.imp_uid}",
            headers={"Authorization": access_token}
        )
        payment_data = payment_response.json()

        if payment_response.status_code != 200 or "response" not in payment_data:
            raise HTTPException(status_code=400, detail="결제 내역 조회에 실패했습니다.")

        actual_payment = payment_data["response"]

        # 3. 가맹점 DB에서 상품의 진짜 원래 가격 조회하기 (예시: 1,000원)
        # order = db.query(Order).filter(Order.merchant_uid == data.merchant_uid).first()
        # amount_to_be_paid = order.amount
        amount_to_be_paid = 1000 

        # 4. 결제 위변조 검증 (실제 결제 금액 vs 서버 DB 금액 대조)
        if actual_payment["amount"] == amount_to_be_paid:
            # [검증 성공] 이곳에서 주문 DB 상태를 '결제완료'로 업데이트하세요.
            return {"status": "success", "message": "결제 검증 성공"}
        else:
            # [금액 불일치] 위변조 의심
            raise HTTPException(status_code=400, detail="금액이 위변조되었습니다.")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)