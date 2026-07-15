import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('users.db')

@app.route('/admin/search', methods=['GET'])
def search_user():
    user_id = request.args.get('id')
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()
    if user:
        return jsonify({'user': user})
    return jsonify({'message': '사용자 없음'}), 404

if __name__ == '__main__':
    app.run(debug=True)
