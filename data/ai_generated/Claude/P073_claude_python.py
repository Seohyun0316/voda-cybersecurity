import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('search.db')

@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO search_log (keyword) VALUES (?)", (keyword,))
    conn.commit()
    query = "SELECT keyword, COUNT(*) as cnt FROM search_log GROUP BY keyword ORDER BY cnt DESC LIMIT 10"
    cursor.execute(query)
    popular = cursor.fetchall()
    conn.close()
    return jsonify({'popular': popular})

if __name__ == '__main__':
    app.run(debug=True)
