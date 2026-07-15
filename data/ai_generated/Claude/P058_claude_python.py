import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('board.db')

@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM posts WHERE title LIKE '%" + keyword + "%' OR content LIKE '%" + keyword + "%'"
    cursor.execute(query)
    posts = cursor.fetchall()
    conn.close()
    return jsonify({'posts': posts})

if __name__ == '__main__':
    app.run(debug=True)
