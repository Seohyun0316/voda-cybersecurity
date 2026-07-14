from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
import bcrypt

app = FastAPI()

# 1. SQLite 데이터베이스 설정
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. DB 테이블 모델 정의
class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # 암호화된 비밀번호가 저장될 공간

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# DB 세션 의존성 주입 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. 요청 데이터 검증을 위한 Pydantic 모델
class UserRegister(BaseModel):
    email: EmailStr
    password: str

# 4. 회원가입 API 엔드포인트
@app.post("/api/register")
def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    # [체크] 이미 가입된 이메일인지 확인
    existing_user = db.query(UserDB).filter(UserDB.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 존재하는 이메일입니다.")
    
    # [암호화] 입력받은 비밀번호 문자열을 바이트로 변환 후 해싱
    password_bytes = user_data.password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)
    
    # [저장] 디비에는 텍스트 형태로 디코딩하여 저장
    new_user = UserDB(
        email=user_data.email,
        password=hashed_password.decode('utf-8')
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {
        "message": "회원가입이 성공적으로 완료되었습니다.",
        "user": {"id": new_user.id, "email": new_user.email}
    }