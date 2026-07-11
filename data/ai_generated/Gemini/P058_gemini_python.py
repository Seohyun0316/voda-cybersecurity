import sqlite3

def search_posts(keyword):
    # 1. 데이터베이스 연결 (예시: 메모리 DB 또는 파일 DB)
    conn = sqlite3.connect(':memory:')  # 실제 사용 시 'database.db'
    cursor = conn.cursor()
    
    # 임시 테이블 및 데이터 생성 (테스트용)
    cursor.execute("CREATE TABLE posts (id INTEGER, title TEXT, content TEXT)")
    cursor.execute("INSERT INTO posts VALUES (1, '사과 맛있어요', '오늘 아침에 사과를 먹었다.')")
    cursor.execute("INSERT INTO posts VALUES (2, '바나나 길다', '바나나는 길어 길으면 기차')")
    cursor.execute("INSERT INTO posts VALUES (3, '질문입니다', '사과 고르는 법 아시는 분?')")

    # 2. 쿼리 작성 (SQL Injection 방지를 위해 플레이스홀더 '?' 사용)
    query = """
        SELECT * FROM posts 
        WHERE title LIKE ? 
           OR content LIKE ?
    """
    
    # 3. 입력값 전후로 %를 붙여 파라미터 전달 (튜플 형태)
    # LIKE 연산자에 들어갈 양식('%키워드%')을 파이썬에서 만들어 줍니다.
    search_keyword = f"%{keyword}%"
    
    # 두 개의 '?' 자리에 각각 search_keyword가 안전하게 대입됩니다.
    cursor.execute(query, (search_keyword, search_keyword))
    
    # 4. 결과 가져오기
    results = cursor.fetchall()
    
    # 연결 종료
    conn.close()
    
    return results

# 실행 테스트
search_word = "사과"
posts = search_posts(search_word)

print(f"--- '{search_word}' 검색 결과 ---")
for post in posts:
    print(f"ID: {post[0]} | 제목: {post[1]} | 내용: {post[2]}")