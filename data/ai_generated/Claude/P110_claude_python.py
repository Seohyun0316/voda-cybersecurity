import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('delivery.db')

@app.route('/track')
def track():
    phone = request.args.get('phone', '')
    conn = get_db()
    result = conn.execute('SELECT * FROM deliveries WHERE phone=?', (phone,)).fetchall()
    conn.close()
    return jsonify({'deliveries': result})

@app.errorhandler(Exception)
def handle_error(e):
    return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
