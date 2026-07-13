from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML = """
<!doctype html>
<html>
<body>
    <h2>파일 업로드</h2>

    <form method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <input type="submit" value="업로드">
    </form>

    {% if message %}
        <p>{{ message }}</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def upload():
    message = ""

    if request.method == "POST":
        file = request.files.get("file")

        if file and file.filename:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            message = f"{filename} 업로드 완료"

    return render_template_string(HTML, message=message)

if __name__ == "__main__":
    app.run(debug=True)