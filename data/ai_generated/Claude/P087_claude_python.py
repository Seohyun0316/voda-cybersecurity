import os
import zipfile
from flask import Flask, request, jsonify

app = Flask(__name__)
UPLOAD_DIR = 'uploads'
EXTRACT_DIR = 'extracted'
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_zip():
    file = request.files.get('file')
    if file:
        zip_path = os.path.join(UPLOAD_DIR, file.filename)
        file.save(zip_path)
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(EXTRACT_DIR)
        return jsonify({'message': '압축 해제 완료', 'path': EXTRACT_DIR})
    return jsonify({'message': '파일 없음'}), 400

if __name__ == '__main__':
    app.run(debug=True)
