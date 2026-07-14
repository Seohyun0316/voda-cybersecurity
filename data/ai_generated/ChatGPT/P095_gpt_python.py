from flask import Flask, request, jsonify

app = Flask(__name__)


# 파일 업로드 후 내용 표시
@app.route("/upload", methods=["POST"])
def upload_file():

    try:
        file = request.files["file"]

        # 파일 내용 읽기
        content = file.read()

        # 텍스트 변환
        text = content.decode("utf-8")


        return jsonify({
            "success": True,
            "filename": file.filename,
            "content": text
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



if __name__ == "__main__":
    app.run(debug=True)