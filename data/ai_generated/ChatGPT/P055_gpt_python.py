from flask import Flask, request, render_template_string

app = Flask(__name__)

comments = []

HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>´ñ±Û ¿¹Á¦</title>
</head>
<body>
    <h2>´ñ±Û</h2>

    <form method="post">
        <input type="text" name="comment" placeholder="´ñ±ÛÀ» ÀÔ·ÂÇÏ¼¼¿ä" required>
        <input type="submit" value="µî·Ï">
    </form>

    <hr>

    {% for comment in comments %}
        <p>{{ comment }}</p>
    {% endfor %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        comment = request.form["comment"]
        comments.append(comment)

    return render_template_string(HTML, comments=comments)

if __name__ == "__main__":
    app.run(debug=True)