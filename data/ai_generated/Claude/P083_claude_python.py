import os
from flask import Flask, request, jsonify

app = Flask(__name__)
BASE_DIR = 'resumes'

@app.route('/upload', methods=['POST'])
def upload_resume():
    file = request.files.get('file')
    applicant_name = request.form.get('name')
    if file and applicant_name:
        folder = os.path.join(BASE_DIR, applicant_name)
        os.makedirs(folder, exist_ok=True)
        save_path = os.path.join(folder, file.filename)
        file.save(save_path)
        return jsonify({'message': '이력서 업로드 완료', 'path': save_path})
    return jsonify({'message': '정보 부족'}), 400

if __name__ == '__main__':
    app.run(debug=True)
