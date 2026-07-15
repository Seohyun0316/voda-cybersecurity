import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['DEBUG'] = True

def get_db():
    return sqlite3.connect('clinic.db')

@app.route('/appointment', methods=['POST'])
def make_appointment():
    data = request.get_json()
    patient_name = data.get('patient_name')
    rrn = data.get('rrn')
    phone = data.get('phone')
    date = data.get('date')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS appointments (patient_name, rrn, phone, date)')
    cursor.execute('INSERT INTO appointments VALUES (?, ?, ?, ?)', (patient_name, rrn, phone, date))
    conn.commit()
    conn.close()
    return jsonify({'message': '예약 완료'})

if __name__ == '__main__':
    app.run(debug=True)
