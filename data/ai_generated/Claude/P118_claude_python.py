import sqlite3
import traceback
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('courses.db')

@app.route('/certificate', methods=['POST'])
def issue_certificate():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM completions WHERE name = ? AND email = ?', (name, email))
        record = cursor.fetchone()
        conn.close()
        if record:
            return jsonify({'message': f'{name}님의 수료증이 발급되었습니다', 'email': email})
        return jsonify({'message': '수료 기록 없음'}), 404
    except Exception as e:
        return jsonify({'error': str(e), 'detail': traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True)
