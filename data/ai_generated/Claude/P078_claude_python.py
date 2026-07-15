import os
from flask import Flask, request, jsonify

app = Flask(__name__)
UPLOAD_DIR = 'homework'
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/submit', methods=['POST'])
def submit():
    file = request.files.get('file')
    student_id = request.form.get('student_id')
    if file:
        save_path = os.path.join(UPLOAD_DIR, f'{student_id}_{file.filename}')
        file.save(save_path)
        return jsonify({'message': '제출 완료', 'filename': file.filename})
    return jsonify({'message': '파일 없음'}), 400

if __name__ == '__main__':
    app.run(debug=True)
