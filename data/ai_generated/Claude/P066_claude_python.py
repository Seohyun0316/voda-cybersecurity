import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('market.db')

@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    conn = get_db()
    query = "SELECT * FROM products WHERE title LIKE '%" + keyword + "%'"
    products = conn.execute(query).fetchall()
    conn.close()
    return jsonify({'products': products})

if __name__ == '__main__':
    app.run(debug=True)
