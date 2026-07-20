from flask import Flask, request, jsonify
import os
import zipfile

app = Flask(__name__)

UPLOAD_DIR = "uploads"
EXTRACT_DIR = "extracted"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)


def safe_extract(zip_path, extract_path):
    with zipfile.ZipFile(zip_path, "r") as z:
        for member in z.infolist():
            # 경로 조작 방지
            target_path = os.path.abspath(
                os.path.join(extract_path, member.filename)
            )

            if not target_path.startswith(
                os.path.abspath(extract_path)
            ):
                raise Exception("잘못된 압축 경로")

        z.extractall(extract_path)


@app.route("/upload", methods=["POST"])
def upload_zip():
    file = request.files["file"]

    zip_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    file.save(zip_path)

    safe_extract(
        zip_path,
        EXTRACT_DIR
    )

    return jsonify({
        "message": "압축 해제 완료"
    })


if __name__ == "__main__":
    app.run(debug=True)