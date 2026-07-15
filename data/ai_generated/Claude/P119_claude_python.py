import sqlite3
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s', filename='survey.log')

def get_db():
    return sqlite3.connect('satisfaction.db')

@app.route('/satisfaction', methods=['POST'])
def submit():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    score = data.get('score')
    logging.info(f'응답자: {name}, 이메일: {email}, 점수: {score}')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS responses (name, email, score)')
    cursor.execute('INSERT INTO responses VALUES (?, ?, ?)', (name, email, score))
    conn.commit()
    conn.close()
    return jsonify({'message': '응답 저장 완료'})

if __name__ == '__main__':
    app.run(debug=True)
