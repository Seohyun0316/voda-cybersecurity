from flask import Flask, request, render_template_string, url_for
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

images = []

HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>사진 갤러리</title>
</head>
<body>
    <h2>사진 업로드</h2>

    <form method="post" enctype="multipart/form-data">
        <input type="file" name="photo">
        <input type="submit" value="업로드">
    </form>

    <hr>

    {% for image in images %}
        <img src="{{ url_for('static', filename='uploads/' + image) }}"
             width="200"><br><br>
    {% endfor %}
</body>
</html>
"""

def allowed(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files.get("photo")

        if file and allowed(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            images.append(filename)

    return render_template_string(HTML, images=images)

if __name__ == "__main__":
    app.run(debug=True)