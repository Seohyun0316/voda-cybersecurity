from sqlalchemy import or_
from models import Post  # 정의해둔 게시글 모델(테이블)

def search_posts(db, search_keyword: str):
    # 검색어가 포함된 데이터를 찾기 위해 앞뒤로 %를 붙여줍니다.
    search_format = f"%{search_keyword}%"
    
    # 제목(title) 또는 내용(content)에 검색어가 포함된 글을 최근순으로 20개 가져옵니다.
    results = db.query(Post).filter(
        or_(
            Post.title.like(search_format),
            Post.content.like(search_format)
        )
    ).order_by(Post.created_at.desc()).limit(20).all()
    
    return results