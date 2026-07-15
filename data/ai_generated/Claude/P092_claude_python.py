import os
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)
FILE_DIR = 'resources'
os.makedirs(FILE_DIR, exist_ok=True)

@app.route('/admin/upload', methods=['POST'])
def admin_upload():
    file = request.files.get('file')
    if file:
        file.save(os.path.join(FILE_DIR, file.filename))
        return jsonify({'message': '업로드 성공'})
    return jsonify({'message': '파일 없음'}), 400

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(FILE_DIR, filename, as_attachment=True)

@app.route('/files')
def list_files():
    files = os.listdir(FILE_DIR)
    return jsonify({'files': files})

if __name__ == '__main__':
    app.run(debug=True)
