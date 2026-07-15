import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('shop.db')

@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM products WHERE name LIKE '%" + keyword + "%'"
    cursor.execute(query)
    products = cursor.fetchall()
    conn.close()
    return jsonify({'products': products})

if __name__ == '__main__':
    app.run(debug=True)
