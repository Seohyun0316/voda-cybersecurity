import os
from flask import Flask, request, send_file

app = Flask(__name__)
FILE_DIR = '/var/www/downloads'

@app.route('/download')
def download():
    filename = request.args.get('file', '')
    filepath = os.path.join(FILE_DIR, filename)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
