from flask import Flask, request, render_template_string

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":
        name = request.form["name"]
        message = f"안녕하세요, {name}님!"

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>인사 페이지</title>
    </head>
    <body>

        <h1>이름 입력</h1>

        <form method="post">
            <input type="text" name="name" placeholder="이름">
            <button type="submit">확인</button>
        </form>

        <h2>{{ message }}</h2>

    </body>
    </html>
    """

    return render_template_string(
        html,
        message=message
    )


if __name__ == "__main__":
    app.run(debug=True)