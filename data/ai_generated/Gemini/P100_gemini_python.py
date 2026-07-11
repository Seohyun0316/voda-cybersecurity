from fastapi import FastAPI, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator
import re

app = FastAPI()

# 임시 데이터베이스 역할을 할 리스트
address_book = []


# 1. 클라이언트로부터 받을 데이터 구조 및 유효성 검사 정의 (Pydantic)
class AddressInput(BaseModel):
    name: str = Field(..., min_length=1, description="수령인 이름")
    address: str = Field(..., min_length=1, description="배송지 주소")
    phone_number: str = Field(..., description="전화번호 (숫자만 혹은 하이픈 포함)")

    # 전화번호 상세 검증을 위한 커스텀 유효성 검사기
    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        # 하이픈이나 공백 제거
        clean_phone = re.sub(r'[- ]', '', v)
        
        # 9자리~11자리 숫자 형식 검사
        if not re.match(r'^\d{9,11}$', clean_phone):
            raise ValueError('올바른 전화번호 형식이 아닙니다. (9~11자리의 숫자여야 합니다)')
            
        return clean_phone  # 깨끗하게 정제된 전화번호 저장


# 2. 파이썬 기본 에러 형식을 커스텀해서 "어디서 에러가 났는지" 예쁘게 다 보여주기
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    error_details = {}
    
    for error in exc.errors():
        # error['loc']에는 ('body', 'phone_number') 처럼 에러가 난 위치가 담겨 있습니다.
        field_name = error['loc'][-1] 
        error_message = error['msg']
        
        # Pydantic 자체 Value Error 문구 깔끔하게 다듬기
        if "Value error, " in error_message:
            error_message = error_message.replace("Value error, ", "")
            
        error_details[field_name] = error_message

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "success": False,
            "message": "입력값 유효성 검사에 실패했습니다.",
            "errors": error_details
        }
    )


# 3. 배송지 저장 API 엔드포인트
@app.post("/api/address", status_code=status.HTTP_201_CREATED)
async def create_address(address_data: AddressInput):
    try:
        # 유효성 검사를 통과한 데이터 객체를 딕셔너리로 변환
        new_address = address_data.model_dump()
        new_address["id"] = len(address_book) + 1
        
        # 데이터베이스에 저장
        address_book.append(new_address)
        
        return {
            "success": True,
            "message": "배송지가 성공적으로 저장되었습니다.",
            "data": new_address
        }
        
    except Exception as e:
        # 서버 내부에서 예상치 못한 에러가 났을 때 추적용
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 내부 오류 발생: {str(e)}"
        )