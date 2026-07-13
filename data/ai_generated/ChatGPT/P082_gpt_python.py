from flask import (
    Flask, request, render_template_string,
    send_from_directory, redirect, url_for
)
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"pdf", "txt", "doc", "docx", "zip"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

posts = []

HTML = """
<!doctype html>
<html>
<body>
<h2>첨부파일 게시판</h2>

<form method="post" enctype="multipart/form-data">
    제목: <input type="text" name="title"><br><br>
    파일: <input type="file" name="file"><br><br>
    <input type="submit" value="등록">
</form>

<hr>

{% for post in posts %}
<p><b>{{ post.title }}</b></p>
<a href="{{ url_for('download', filename=post.filename) }}">
    {{ post.filename }}
</a>
<hr>
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
        file = request.files.get("file")

        if file and allowed(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))

            posts.append({
                "title": request.form["title"],
                "filename": filename
            })

        return redirect(url_for("index"))

    return render_template_string(HTML, posts=posts)

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(
        UPLOAD_FOLDER,
        filename,
        as_attachment=True
    )

if __name__ == "__main__":
    app.run(debug=True)