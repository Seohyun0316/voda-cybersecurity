import os
from flask import Flask, request, send_file

app = Flask(__name__)
BASE_DIR = '/var/www/files'

@app.route('/download')
def download():
    filename = request.args.get('filename')
    filepath = os.path.join(BASE_DIR, filename)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
