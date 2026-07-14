from flask import Flask, request, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = "downloads"

@app.route("/download")
def download():
    filename = request.args.get("filename")

    if not filename:
        return "파일명을 입력하세요.", 400

    return send_from_directory(
        UPLOAD_FOLDER,
        filename,
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)