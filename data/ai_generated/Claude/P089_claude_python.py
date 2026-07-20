import csv
import io
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/upload/csv', methods=['POST'])
def upload_csv():
    file = request.files.get('file')
    if file:
        content = file.read().decode('utf-8', errors='ignore')
        reader = csv.DictReader(io.StringIO(content))
        rows = list(reader)
        return jsonify({'rows': rows, 'count': len(rows)})
    return jsonify({'message': '파일 없음'}), 400

if __name__ == '__main__':
    app.run(debug=True)
