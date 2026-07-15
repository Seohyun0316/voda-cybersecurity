import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('blood.db')

@app.route('/apply', methods=['POST'])
def apply():
    data = request.get_json()
    name = data.get('name')
    rrn = data.get('rrn')
    blood_type = data.get('blood_type')
    contact = data.get('contact')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS applications (name, rrn, blood_type, contact)')
    cursor.execute('INSERT INTO applications VALUES (?, ?, ?, ?)', (name, rrn, blood_type, contact))
    conn.commit()
    conn.close()
    return jsonify({'message': '신청 완료'})

if __name__ == '__main__':
    app.run(debug=True)
