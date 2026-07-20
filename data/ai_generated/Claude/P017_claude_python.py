import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('users.db')

@app.route('/admin/users/search')
def search_user():
    user_id = request.args.get('id', '')
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + user_id + "'"
    cursor.execute(query)
    users = cursor.fetchall()
    conn.close()
    return jsonify({'users': users})

if __name__ == '__main__':
    app.run(debug=True)
