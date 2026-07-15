import os
from flask import Flask, request, jsonify

app = Flask(__name__)
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file:
        file.save(os.path.join(UPLOAD_DIR, file.filename))
        return jsonify({'message': '업로드 성공', 'filename': file.filename})
    return jsonify({'message': '파일 없음'}), 400

if __name__ == '__main__':
    app.run(debug=True)
