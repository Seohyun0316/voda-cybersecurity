from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)


# 파일 저장 폴더
UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER



# 관리자 파일 업로드
@app.route("/admin/upload", methods=["POST"])
def upload_file():

    try:
        file = request.files["file"]


        if file:

            filename = file.filename

            save_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            file.save(save_path)


            return jsonify({
                "success": True,
                "message": "파일 업로드 완료",
                "filename": filename
            })


        return jsonify({
            "success": False,
            "message": "파일이 없습니다."
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500




# 자료실 파일 목록 조회
@app.route("/files", methods=["GET"])
def file_list():

    files = os.listdir(
        app.config["UPLOAD_FOLDER"]
    )


    return jsonify({
        "success": True,
        "files": files
    })




# 파일 다운로드
@app.route("/download/<filename>", methods=["GET"])
def download(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )




if __name__ == "__main__":
    app.run(debug=True)