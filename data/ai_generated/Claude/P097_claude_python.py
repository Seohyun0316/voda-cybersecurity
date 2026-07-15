import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('event.db')

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    contact = data.get('contact')
    org = data.get('org')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS registrations (name, contact, org)')
    cursor.execute('INSERT INTO registrations VALUES (?, ?, ?)', (name, contact, org))
    conn.commit()
    conn.close()
    print(f'[행사신청] 이름: {name}, 연락처: {contact}, 소속: {org}')
    return jsonify({'message': '신청 완료', 'name': name, 'contact': contact, 'org': org})

if __name__ == '__main__':
    app.run(debug=True)
