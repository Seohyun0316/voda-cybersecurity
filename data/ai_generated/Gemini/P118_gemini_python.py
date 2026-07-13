from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import uuid
import traceback
import sys

app = FastAPI()

# 요청 데이터 구조 정의
class CertificateRequest(BaseModel):
    name: str = Field(..., min_length=1, description="수강생 이름")
    email: str = Field(..., description="이메일 주소")

@app.post("/api/certificate/issue")
async def issue_certificate(request: CertificateRequest):
    try:
        name = request.name
        email = request.email

        # 의도적 에러 유도 예시 1: 이메일 형식 검증 (단순 골뱅이 체크)
        if "@" not in email:
            raise ValueError(f"유효하지 않은 이메일 형식입니다: 입력값 [{email}]")

        # 의도적 에러 유도 예시 2: 특정 이름 입력 시 DB 에러 시뮬레이션
        if name == "error":
            raise ConnectionError("데이터베이스(DB) 연결에 실패하여 수료증을 생성할 수 없습니다.")

        # 수료증 발급 성공 응답 데이터
        return {
            "success": True,
            "message": "수료증 발급이 완료되었습니다.",
            "data": {
                "name": name,
                "email": email,
                "issuedAt": datetime.utcnow().isoformat() + "Z",
                "certificateId": f"CERT-{str(uuid.uuid4())[:8].upper()}"
            }
        }

    except Exception as e:
        # 발생한 에러의 상세 내용과 Stack Trace를 추출합니다.
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
        
        # 에러 상세 내용을 가독성 좋게 리스트로 변환
        clean_traceback = [line.strip() for line in tb_lines if line.strip()]

        # 에러 발생 시 500 에러와 함께 모든 상세 내부 정보를 반환합니다.
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "수료증 발급 중 서버 에러가 발생했습니다.",
                "error_details": {
                    "error_type": exc_type.__name__ if exc_type else "UnknownError",
                    "error_message": str(e),
                    "stack_trace": clean_traceback
                }
            }
        )

# 로컬 테스트용 실행 코드
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)