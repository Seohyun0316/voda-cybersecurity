import sqlite3

def setup_mock_database():
    """테스트용 임시 메모리 데이터베이스를 만들고 중고거래 샘플 데이터를 넣습니다."""
    # 메모리에 임시 DB 생성
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # products 테이블 생성
    cursor.execute("""
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            price INTEGER NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 테스트용 중고거래 상품 데이터 삽입
    sample_data = [
        ("아이폰 15 프로 256G", 1100000, "상태 아주 좋습니다. 기스 없어요."),
        ("삼천리 하이브리드 자전거", 80000, "출퇴근용으로 타던 자전거 급처합니다."),
        ("맥북 에어 M2 13인치", 950000, "풀박스 구성이며 자전거 타고 직거래 희망해요."),
        ("갤럭시 S24 울트라", 1000000, "액정 깨끗하고 케이스 같이 드립니다.")
    ]
    
    cursor.executemany(
        "INSERT INTO products (title, price, description) VALUES (?, ?, ?)", 
        sample_data
    )
    conn.commit()
    return conn


def search_products(db_connection, keyword: str):
    """실제 검색을 수행하는 함수 (SQL 인젝션 안전)"""
    cursor = db_connection.cursor()
    
    # %검색어% 형태로 검색 패턴 제작
    search_pattern = f"%{keyword}%"
    
    # 제목(title) 또는 설명(description)에서 검색어를 찾아 최신순 정렬
    query = """
        SELECT id, title, price, description, created_at 
        FROM products 
        WHERE title LIKE ? OR description LIKE ?
        ORDER BY created_at DESC
    """
    
    cursor.execute(query, (search_pattern, search_pattern))
    return cursor.fetchall()


# ==========================================
# 실행 테스트 (이 파일을 그냥 실행하시면 됩니다)
# ==========================================
if __name__ == "__main__":
    # 1. 테스트용 임시 DB 세팅
    db = setup_mock_database()
    
    # 2. 검색어 입력 (테스트)
    search_keyword = "자전거"
    print(f"🔍 '{search_keyword}' 검색 결과:")
    print("-" * 50)
    
    # 3. 검색 실행
    results = search_products(db, search_keyword)
    
    # 4. 결과 출력
    if not results:
        print("검색 결과가 없습니다.")
    else:
        for item in results:
            product_id, title, price, description, date = item
            print(f"📦 [{product_id}] {title}")
            print(f"💰 가격: {price:,}원")
            print(f"📝 내용: {description}")
            print(f"📅 등록일: {date}")
            print("-" * 50)
            
    # DB 연결 종료
    db.close()