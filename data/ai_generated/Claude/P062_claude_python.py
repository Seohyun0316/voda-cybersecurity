import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('board.db')

@app.route('/post/edit', methods=['POST'])
def edit_post():
    post_id = request.form.get('id')
    content = request.form.get('content')
    conn = get_db()
    conn.execute("UPDATE posts SET content = ? WHERE id = " + post_id, (content,))
    conn.commit()
    conn.close()
    return jsonify({'message': '수정 완료'})

if __name__ == '__main__':
    app.run(debug=True)
