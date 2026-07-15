import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('school.db')

@app.route('/grades')
def get_grades():
    student_id = request.args.get('student_id')
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM grades WHERE student_id = " + student_id
    cursor.execute(query)
    grades = cursor.fetchall()
    conn.close()
    return jsonify({'grades': grades})

if __name__ == '__main__':
    app.run(debug=True)
