import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('board.db')

@app.route('/posts')
def get_posts():
    page = request.args.get('page', '1')
    per_page = 10
    offset = (int(page) - 1) * per_page
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM posts LIMIT " + str(per_page) + " OFFSET " + page
    cursor.execute(query)
    posts = cursor.fetchall()
    conn.close()
    return jsonify({'posts': posts, 'page': page})

if __name__ == '__main__':
    app.run(debug=True)
