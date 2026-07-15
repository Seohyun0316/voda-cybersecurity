import os
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/files')
def list_files():
    folder = request.args.get('path', '')
    files = os.listdir(folder)
    return jsonify({'path': folder, 'files': files})

if __name__ == '__main__':
    app.run(debug=True)
