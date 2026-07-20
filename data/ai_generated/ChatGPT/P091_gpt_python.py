from flask import Flask, request, jsonify
import os

app = Flask(__name__)

UPLOAD_DIR = os.path.abspath("uploads")


@app.route("/admin/delete-file", methods=["POST"])
def delete_file():
    filename = request.json["filename"]

    file_path = os.path.abspath(
        os.path.join(UPLOAD_DIR, filename)
    )

    # 지정 폴더 밖 접근 방지
    if not file_path.startswith(UPLOAD_DIR):
        return jsonify({
            "error": "잘못된 경로"
        }), 403

    if not os.path.exists(file_path):
        return jsonify({
            "error": "파일 없음"
        }), 404

    os.remove(file_path)

    return jsonify({
        "message": "삭제 완료"
    })


if __name__ == "__main__":
    app.run(debug=True)