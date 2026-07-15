import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('consulting.db')

@app.route('/consult', methods=['POST'])
def consult():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    content = data.get('content')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS consults (name, phone, content)')
    cursor.execute('INSERT INTO consults VALUES (?, ?, ?)', (name, phone, content))
    conn.commit()
    conn.close()
    print(f'[상담접수] 이름: {name}, 전화: {phone}, 내용: {content}')
    return jsonify({'message': '상담 접수 완료'})

if __name__ == '__main__':
    app.run(debug=True)
