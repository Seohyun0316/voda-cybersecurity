from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()

# 1. 모델 정의
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    
    # 관계 설정 (User를 통해 작성글에 바로 접근 가능하게 함)
    posts = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    author = relationship("User", back_populates="posts")

# 2. 데이터베이스 연결 및 세션 생성 (예시: MySQL 연결)
# 'mysql+pymysql://사용자:비밀번호@호스트:포트/데이터베이스명'
engine = create_engine('mysql+pymysql://root:password@localhost:3306/my_database')
Session = sessionmaker(bind=engine)
session = Session()

# 3. 관리자가 회원 아이디로 글을 조회하는 함수
def get_all_posts_by_username(target_username: str):
    # u.username = target_username 인 조건을 걸어 posts를 JOIN 조회합니다.
    results = (
        session.query(Post)
        .join(User)
        .filter(User.username == target_username)
        .all()
    )
    return results

# [사용 예시]
admin_search_username = "user123"
user_posts = get_all_posts_by_username(admin_search_username)

for post in user_posts:
    print(f"제목: {post.title} | 내용: {post.content[:20]}...")