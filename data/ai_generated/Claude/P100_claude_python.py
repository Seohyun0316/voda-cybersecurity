import sqlite3
import traceback
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('delivery.db')

@app.route('/address', methods=['POST'])
def save_address():
    try:
        data = request.get_json()
        name = data.get('name')
        address = data.get('address')
        phone = data.get('phone')
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS addresses (name, address, phone)')
        cursor.execute('INSERT INTO addresses VALUES (?, ?, ?)', (name, address, phone))
        conn.commit()
        conn.close()
        return jsonify({'message': '저장 완료'})
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(debug=True)
