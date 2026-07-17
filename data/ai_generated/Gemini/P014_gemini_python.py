from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
import bcrypt
import uvicorn

app = FastAPI()

# 1. 클라이언트가 보낼 데이터 포맷 정의 (요청 바디)
class SignUpRequest(BaseModel):
    email: EmailStr  # 간단한 이메일 형식 검증 포함
    password: str
    name: str

# 가짜 DB 실행 함수 (실제 쓰시는 DB 라이브러리로 대체해줘!)
def save_to_db(email, hashed_password, name):
    # 예: "INSERT INTO users (email, password, name) VALUES (%s, %s, %s)"
    # sql_execute(query, (email, hashed_password, name))
    pass

@app.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_data: SignUpRequest):
    # 2. 비밀번호 암호화 (해싱)
    # bcrypt는 bytes 타입을 요구하므로 encode()가 필요해
    password_bytes = user_data.password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    try:
        # 3. DB에 그대로 넣기
        save_to_db(user_data.email, hashed_password, user_data.name)
        return {"message": "회원가입이 완료되었습니다."}
        
    except Exception as e:
        # 이메일 중복 등의 에러가 발생했을 때 처리
        # (실제 DB 에러 코드에 맞게 분기 처리해주면 좋아!)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="이미 등록된 이메일이거나 회원가입에 실패했습니다."
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)