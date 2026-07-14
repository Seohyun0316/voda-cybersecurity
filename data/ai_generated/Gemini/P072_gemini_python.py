from fastapi import FastAPI, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

app = FastAPI()

@app.get("/posts")
def get_posts(
    # page 파라미터를 int 타입으로 강제하고, 기본값을 1로 설정 (최소값 1 제한)
    page: int = Query(default=1, ge=1), 
    limit: int = 10
):
    offset = (page - 1) * limit

    # ❌ 위험한 방식 (SQL 인젝션 취약)
    # query = f"SELECT * FROM posts LIMIT {limit} OFFSET {offset}"
    
    # 
    # text() 내부에 :limit, :offset 처럼 플레이스홀더를 두고, bindparams로 값을 넘깁니다.
    query = text("SELECT * FROM posts ORDER BY id DESC LIMIT :limit OFFSET :offset")
    
    # 예시를 위한 가상 실행 코드 (실제 변수 바인딩 처리)
    # db.execute(query, {"limit": limit, "offset": offset}).fetchall()
    
    return {"page": page, "offset": offset, "message": "안전하게 쿼리가 준비되었습니다."}