from flask import Flask, request, jsonify
import csv
import io

app = Flask(__name__)

# 업로드 크기 제한 (예: 10MB)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


@app.route("/upload-csv", methods=["POST"])
def upload_csv():
    file = request.files["file"]

    # CSV 읽기
    stream = io.TextIOWrapper(
        file.stream,
        encoding="utf-8"
    )

    reader = csv.DictReader(stream)

    rows = []

    for row in reader:
        rows.append(row)

    return jsonify({
        "count": len(rows),
        "data": rows
    })


if __name__ == "__main__":
    app.run(debug=True)