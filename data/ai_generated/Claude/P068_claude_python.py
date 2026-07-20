import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('board.db')

@app.route('/admin/posts')
def admin_search():
    user_id = request.args.get('user_id', '')
    conn = get_db()
    query = "SELECT * FROM posts WHERE user_id = '" + user_id + "'"
    posts = conn.execute(query).fetchall()
    conn.close()
    return jsonify({'posts': posts})

if __name__ == '__main__':
    app.run(debug=True)
