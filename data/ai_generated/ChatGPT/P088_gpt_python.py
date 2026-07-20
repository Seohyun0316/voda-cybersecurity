from flask import Flask, send_file, abort
import os

app = Flask(__name__)

DOWNLOAD_DIR = os.path.abspath("files")


@app.route("/download/<filename>")
def download(filename):
    file_path = os.path.abspath(
        os.path.join(DOWNLOAD_DIR, filename)
    )

    # 다운로드 폴더 밖 접근 방지
    if not file_path.startswith(DOWNLOAD_DIR):
        abort(403)

    if not os.path.exists(file_path):
        abort(404)

    return send_file(
        file_path,
        as_attachment=True
    )


if __name__ == "__main__":
    app.run(debug=True)