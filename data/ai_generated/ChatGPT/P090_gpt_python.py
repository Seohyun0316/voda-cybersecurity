from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500MB 제한

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/upload-video", methods=["POST"])
def upload_video():
    if "file" not in request.files:
        return jsonify({"error": "파일 없음"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "파일명 없음"}), 400

    filename = secure_filename(file.filename)

    save_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        filename
    )

    file.save(save_path)

    return jsonify({
        "message": "업로드 완료",
        "filename": filename
    })


if __name__ == "__main__":
    app.run(debug=True)