from fastapi import FastAPI, Depends, Query
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List

# 1. DB 설정 (가장 간단한 SQLite 사용)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. 회원 모델 정의
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String)

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI()

# DB 세션 의존성 생성을 위한 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 3. 회원 검색 API (핵심 쿼리)
@app.get("/admin/users/search")
def search_users(name: str = Query(..., description="검색할 이름"), db: Session = Depends(get_db)):
    # SQL의 WHERE name LIKE '%검색어%' 와 같은 쿼리를 실행합니다.
    users = db.query(User).filter(User.name.contains(name)).all()
    return users