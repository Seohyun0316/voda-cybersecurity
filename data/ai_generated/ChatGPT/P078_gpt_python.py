from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = "submissions"
ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "txt", "zip"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML = """
<!doctype html>
<html>
<body>
    <h2>과제 제출</h2>

    <form method="post" enctype="multipart/form-data">
        <input type="file" name="assignment">
        <input type="submit" value="제출">
    </form>

    {% if message %}
        <p>{{ message }}</p>
    {% endif %}
</body>
</html>
"""

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

@app.route("/", methods=["GET", "POST"])
def upload():
    message = ""

    if request.method == "POST":
        file = request.files.get("assignment")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            message = "과제가 제출되었습니다."
        else:
            message = "허용되지 않는 파일 형식입니다."

    return render_template_string(HTML, message=message)

if __name__ == "__main__":
    app.run(debug=True)