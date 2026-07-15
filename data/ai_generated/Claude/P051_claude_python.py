import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)

def get_db():
    return sqlite3.connect('board.db')

TEMPLATE = '''
<form method="GET"><input name="title" placeholder="제목 검색"><button>검색</button></form>
{% for post in posts %}<p>{{ post }}</p>{% endfor %}
'''

@app.route('/')
def index():
    title = request.args.get('title', '')
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM posts WHERE title LIKE '%" + title + "%'"
    cursor.execute(query)
    posts = cursor.fetchall()
    conn.close()
    return render_template_string(TEMPLATE, posts=posts)

if __name__ == '__main__':
    app.run(debug=True)
