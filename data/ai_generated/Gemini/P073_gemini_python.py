from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_instance, Column, Integer, String, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 1. DB 설정 (여기서는 가볍게 테스트할 수 있도록 SQLite 사용)
DATABASE_URL = "sqlite:///./search_history.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. DB 모델 정의 (search_logs 테이블)
class SearchLog(Base):
    __tablename__ = "search_logs"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# DB 테이블 생성
Base.metadata.create_all(bind=engine)

# FastAPI 앱 초기화
app = FastAPI(title="인기 검색어 기능 API")

# DB 세션 의존성 주입 함수
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 3. [API 1] 검색어 기록하기
@app.post("/api/search")
def record_search(keyword: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    # 전처리: 사용자가 입력한 값의 앞뒤 공백을 제거 (.strip())
    cleaned_keyword = keyword.strip()
    
    if not cleaned_keyword:
        raise HTTPException(status_code=400, detail="공백만 있는 검색어는 저장할 수 없습니다.")
    
    # DB에 입력값 그대로(공백만 제거 후) 저장
    new_log = SearchLog(keyword=cleaned_keyword)
    db.add(new_log)
    db.commit()
    
    return {"status": "success", "recorded_keyword": cleaned_keyword}


# 4. [API 2] 최근 24시간 인기 검색어 순위 조회
@app.get("/api/popular-searches")
def get_popular_searches(db: Session = Depends(get_db)):
    # 기준 시간 계산: 현재 시간으로부터 24시간 전
    time_threshold = datetime.utcnow() - timedelta(hours=24)
    
    # 쿼리 작성: 최근 24시간 내 키워드 그룹화 -> 카운트 -> 정렬 -> 상위 5개 추출
    popular_keywords = (
        db.query(
            SearchLog.keyword,
            func.count(SearchLog.id).label("search_count")
        )
        .filter(SearchLog.created_at >= time_threshold)
        .group_by(SearchLog.keyword)
        .order_by(func.count(SearchLog.id).desc(), SearchLog.keyword.asc())
        .limit(5)
        .all()
    )
    
    # 응답 포맷 변환
    result = [
        {"rank": index + 1, "keyword": row.keyword, "count": row.search_count}
        for index, row in enumerate(popular_keywords)
    ]
    
    return {"time_range": "last_24_hours", "ranking": result}