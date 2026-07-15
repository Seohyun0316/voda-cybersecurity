import sqlite3
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

def get_db():
    return sqlite3.connect('hospital.db')

@app.route('/reserve', methods=['POST'])
def reserve():
    data = request.get_json()
    name = data.get('name')
    rrn = data.get('rrn')
    symptom = data.get('symptom')
    logging.debug(f'[예약] 이름={name}, 주민번호={rrn}, 증상={symptom}')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS reservations (name, rrn, symptom)')
    cursor.execute('INSERT INTO reservations VALUES (?, ?, ?)', (name, rrn, symptom))
    conn.commit()
    conn.close()
    return jsonify({'message': '예약 완료'})

if __name__ == '__main__':
    app.run(debug=True)
