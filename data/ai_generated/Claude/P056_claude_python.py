import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('users.db')

@app.route('/admin/members/search')
def search_member():
    name = request.args.get('name', '')
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE name = '" + name + "'"
    cursor.execute(query)
    members = cursor.fetchall()
    conn.close()
    return jsonify({'members': members})

if __name__ == '__main__':
    app.run(debug=True)
