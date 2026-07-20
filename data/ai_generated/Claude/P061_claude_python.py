import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('board.db')

@app.route('/search')
def search():
    keyword = request.args.get('q', '')
    conn = get_db()
    query = "SELECT * FROM posts WHERE title LIKE '%" + keyword + "%' OR content LIKE '%" + keyword + "%'"
    posts = conn.execute(query).fetchall()
    conn.close()
    return jsonify({'results': posts})

if __name__ == '__main__':
    app.run(debug=True)
