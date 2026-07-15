import csv
import os
from flask import Flask, request, jsonify

app = Flask(__name__)
CSV_FILE = 'enrollments.csv'

@app.route('/enroll', methods=['POST'])
def enroll():
    data = request.get_json()
    student_id = data.get('student_id')
    name = data.get('name')
    contact = data.get('contact')
    print(f'학번: {student_id}, 이름: {name}, 연락처: {contact}')
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['학번', '이름', '연락처'])
        writer.writerow([student_id, name, contact])
    return jsonify({'message': '수강신청 완료', 'student_id': student_id, 'name': name, 'contact': contact})

if __name__ == '__main__':
    app.run(debug=True)
