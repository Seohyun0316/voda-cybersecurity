import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('survey.db')

@app.route('/survey', methods=['POST'])
def submit_survey():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    age = data.get('age')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS survey (name, phone, email, age)')
    cursor.execute('INSERT INTO survey VALUES (?, ?, ?, ?)', (name, phone, email, age))
    conn.commit()
    conn.close()
    print(f'이름: {name}, 전화: {phone}, 이메일: {email}, 나이: {age}')
    return jsonify({'name': name, 'phone': phone, 'email': email, 'age': age})

if __name__ == '__main__':
    app.run(debug=True)
