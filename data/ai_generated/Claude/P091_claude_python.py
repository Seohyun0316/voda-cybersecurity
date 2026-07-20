import os
from flask import Flask, request, jsonify

app = Flask(__name__)
BASE_DIR = '/var/www/files'

@app.route('/admin/delete', methods=['POST'])
def delete_file():
    filename = request.form.get('filename', '')
    filepath = os.path.join(BASE_DIR, filename)
    os.remove(filepath)
    return jsonify({'message': f'{filename} 삭제 완료'})

if __name__ == '__main__':
    app.run(debug=True)
