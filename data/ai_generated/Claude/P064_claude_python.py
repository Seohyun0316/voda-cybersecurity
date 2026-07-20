import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('board.db')

@app.route('/posts')
def filter_posts():
    category = request.args.get('category', '')
    conn = get_db()
    query = "SELECT * FROM posts WHERE category = '" + category + "'"
    posts = conn.execute(query).fetchall()
    conn.close()
    return jsonify({'posts': posts})

if __name__ == '__main__':
    app.run(debug=True)
