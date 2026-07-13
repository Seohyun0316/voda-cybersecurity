from flask import Flask, request, render_template_string
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML = """
<!doctype html>
<html>
<body>
    <h2>프로필 사진 업로드</h2>

    <form method="post" enctype="multipart/form-data">
        <input type="file" name="photo">
        <input type="submit" value="업로드">
    </form>

    {% if message %}
        <p>{{ message }}</p>
    {% endif %}
</body>
</html>
"""

def allowed_file(filename):
    return "." in filename and \
           filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def upload():
    message = ""

    if request.method == "POST":
        file = request.files.get("photo")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            message = "업로드 완료!"
        else:
            message = "이미지 파일만 업로드할 수 있습니다."

    return render_template_string(HTML, message=message)

if __name__ == "__main__":
    app.run(debug=True)