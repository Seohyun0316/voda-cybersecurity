from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>환영 페이지</title>
</head>
<body>
    <form method="post">
        이름: <input type="text" name="name">
        <input type="submit" value="확인">
    </form>

    {% if name %}
        <h2>{{ name }}님 환영합니다.</h2>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    name = ""

    if request.method == "POST":
        name = request.form["name"]

    return render_template_string(HTML, name=name)

if __name__ == "__main__":
    app.run(debug=True)