from fastapi import FastAPI, HTTPException, status
import sqlite3

app = FastAPI()

# DB 연결 헬퍼 함수
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row  # 결과를 딕셔너리 형태로 받기 위함
    return conn

@app.get("/posts/{post_id}")
def read_post(post_id: int):  # 1. 여기서 post_id가 정수(int)가 아니면 FastAPI가 알아서 422 에러를 반환합니다.
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 2. 파라미터 바인딩 사용 (sqlite3는 ? 기호를 사용합니다)
    # SQL 인젝션을 원천 차단하는 가장 안전한 방식입니다.
    sql = "SELECT id, title, content FROM posts WHERE id = ?"
    cursor.execute(sql, (post_id,))  # 튜플 형태로 전달해야 하므로 쉼표(,) 필수
    
    post = cursor.fetchone()
    conn.close()
    
    # 3. 데이터가 존재하지 않는 경우 예외 처리
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="존재하지 않는 게시글입니다."
        )
        
    return dict(post)