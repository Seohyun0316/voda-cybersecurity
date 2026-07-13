from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)

UPLOAD_ROOT = Path("resumes")
UPLOAD_ROOT.mkdir(exist_ok=True)

HTML = """
<!doctype html>
<html>
<body>
<h2>이력서 업로드</h2>

<form method="post" enctype="multipart/form-data">
    지원자 이름:
    <input type="text" name="name"><br><br>

    이력서:
    <input type="file" name="resume"><br><br>

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
        name = secure_filename(request.form["name"])
        file = request.files.get("resume")

        if name and file and file.filename:
            user_dir = UPLOAD_ROOT / name
            user_dir.mkdir(exist_ok=True)

            filename = secure_filename(file.filename)
            file.save(user_dir / filename)

            message = "업로드 완료!"

    return render_template_string(HTML, message=message)

if __name__ == "__main__":
    app.run(debug=True)