import os
from flask import Flask, request, jsonify

app = Flask(__name__)
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file:
        save_path = os.path.join(UPLOAD_DIR, file.filename)
        file.save(save_path)
        return jsonify({'message': '저장 완료', 'path': save_path})
    return jsonify({'message': '파일 없음'}), 400

if __name__ == '__main__':
    app.run(debug=True)
