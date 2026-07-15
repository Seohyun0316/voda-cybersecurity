import os
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)
UPLOAD_DIR = 'attachments'
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if file:
        path = os.path.join(UPLOAD_DIR, file.filename)
        file.save(path)
        return jsonify({'message': '업로드 성공', 'filename': file.filename})
    return jsonify({'message': '파일 없음'}), 400

@app.route('/download')
def download():
    filename = request.args.get('filename')
    path = os.path.join(UPLOAD_DIR, filename)
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
