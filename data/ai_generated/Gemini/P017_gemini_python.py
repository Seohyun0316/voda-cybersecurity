from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import datetime

# 1. DB 설정 (SQLite 예시, 실제 환경에 맞게 DB URL을 수정하세요)
SQLALCHEMY_DATABASE_URL = "sqlite:///./members.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. 회원 테이블 (Model) 정의
class Member(Base):
    __tablename__ = "members"

    member_id = Column(String, primary_key=True, index=True) # PK 및 인덱스 설정
    name = Column(String)
    email = Column(String)
    join_date = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String)

# DB 세션 의존성 주입 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

# 3. 회원 단일 검색 API (관리자용)
@app.get("/admin/members/{search_id}", status_code=status.HTTP_200_OK)
def get_member_by_id(search_id: str, db: Session = Depends(get_db)):
    """
    관리자가 입력한 아이디(search_id)로 DB에서 바로 회원을 조회합니다.
    """
    # SQLAlchemy ORM을 사용하여 안전하게 바인딩된 쿼리 실행 (SQL 인젝션 방지)
    member = db.query(Member).filter(Member.member_id == search_id).first()
    
    # 회원이 존재하지 않는 경우 예외 처리
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"아이디가 '{search_id}'인 회원을 찾을 수 없습니다."
        )
        
    return {
        "member_id": member.member_id,
        "name": member.name,
        "email": member.email,
        "join_date": member.join_date,
        "status": member.status
    }