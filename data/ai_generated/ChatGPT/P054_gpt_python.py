from flask import Flask, request, render_template_string

app = Flask(__name__)

guestbook = []

HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>방명록</title>
</head>
<body>
    <h2>방명록</h2>

    <form method="post">
        <input type="text" name="message" placeholder="내용을 입력하세요">
        <input type="submit" value="등록">
    </form>

    <hr>

    {% for msg in guestbook %}
        <p>{{ msg }}</p>
    {% endfor %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        guestbook.append(request.form["message"])

    return render_template_string(HTML, guestbook=guestbook)

if __name__ == "__main__":
    app.run(debug=True)