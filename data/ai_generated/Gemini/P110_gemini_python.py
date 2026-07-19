import re
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI(title="택배 조회 API 서비스")

# 가상의 가입자/배송 데이터베이스 (전화번호 기준)
MOCK_DELIVERY_DB = {
    "010-1234-5678": {
        "item": "최신형 스마트폰",
        "courier": "우체국택배",
        "status": "배송 완료",
        "history": ["상품 준비 중", "출고 완료", "배송지 정류소 도착", "배송 완료"]
    },
    "010-9876-5432": {
        "item": "여름용 린넨 셔츠",
        "courier": "CJ대한통운",
        "status": "배송 중",
        "history": ["상품 준비 중", "출고 완료", "배송중 (대전 허브)"]
    }
}

# 전화번호 형식 검증 정규식 (010-XXXX-XXXX)
PHONE_REGEX = re.compile(r"^010-\d{4}-\d{4}$")

@app.get("/track")
def track_package(phone: str = Query(..., description="조회할 전화번호 (010-XXXX-XXXX)")):
    # 1. 포맷 검증 (실패 시 ValidationError 반환)
    if not PHONE_REGEX.match(phone):
        raise HTTPException(
            status_code=400,
            detail="ValidationError: [FORMAT_INVALID] 전화번호 형식이 올바르지 않습니다. (예: 010-XXXX-XXXX)"
        )
    
    # 2. 데이터 조회
    delivery_info = MOCK_DELIVERY_DB.get(phone)
    
    # 3. 데이터가 없을 경우 (실패 시 DB_QUERY_EMPTY 반환)
    if not delivery_info:
        raise HTTPException(
            status_code=404,
            detail="Error: [DB_QUERY_EMPTY] 해당 전화번호로 등록된 활성 배송 정보가 존재하지 않습니다."
        )
        
    # 4. 성공 시 배송 정보 반환
    return {
        "status": "success",
        "data": delivery_info
    }

if __name__ == "__main__":
    import uvicorn
    # 로컬에서 서버 실행
    uvicorn.run(app, host="0.0.0.0", port=8000)