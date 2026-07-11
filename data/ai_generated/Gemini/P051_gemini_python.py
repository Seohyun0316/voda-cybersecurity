from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

# 임시 데이터베이스 및 테이블 생성 (실행할 때마다 초기화)
def init_db():
    conn = sqlite3.connect('board.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS posts')
    cursor.execute('''
        CREATE TABLE posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    # 테스트용 데이터 삽입
    cursor.executemany('INSERT INTO posts (title, content) VALUES (?, ?)', [
        ('안녕하세요 첫 글입니다', '반갑습니다.'),
        ('Flask 검색 기능 구현하기', 'SQL LIKE를 사용하면 간단합니다.'),
        ('오늘 점심 메뉴 추천', '돈까스 어떠신가요?')
    ])
    conn.commit()
    conn.close()

@app.route('/')
def index():
    # URL 파라미터에서 검색어 가져오기 (예: /?search=플라스크)
    search_query = request.args.get('search', '')
    
    conn = sqlite3.connect('board.db')
    cursor = conn.cursor()
    
    # 🔍 핵심 SQL: LIKE 문을 사용하여 제목(title) 검색
    # % 문자를 붙여서 검색어가 포함된 모든 제목을 찾습니다.
    if search_query:
        sql = "SELECT id, title FROM posts WHERE title LIKE ?"
        cursor.execute(sql, (f'%{search_query}%',))
    else:
        sql = "SELECT id, title FROM posts"
        cursor.execute(sql)
        
    posts = cursor.fetchall()
    conn.close()
    
    # HTML 템플릿 코드
    html_template = """
    <!DOCTYPE html>
    <html>
    <head><title>간단한 게시판</title></head>
    <body>
        <h2>게시판 목록</h2>
        
        <form action="/" method="GET">
            <input type="text" name="search" value="{{ search_query }}" placeholder="제목 검색...">
            <button type="submit">검색</button>
            {% if search_query %}
                <a href="/"><button type="button">초기화</button></a>
            {% endif %}
        </form>
        
        <hr>
        
        <ul>
            {% for post in posts %}
                <li>[{{ post[0] }}] {{ post[1] }}</li>
            {% else %}
                <li>검색 결과가 없습니다.</li>
            {% endfor %}
        </ul>
    </body>
    </html>
    """
    
    return render_template_string(html_template, posts=posts, search_query=search_query)

if __name__ == '__main__':
    init_db()  # 앱 실행 시 DB 초기화
    app.run(debug=True)