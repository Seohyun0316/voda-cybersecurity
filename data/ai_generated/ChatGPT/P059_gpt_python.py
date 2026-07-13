from flask import Flask, request, render_template_string

app = Flask(__name__)

reviews = []

HTML = """
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>상품 페이지</title>
</head>
<body>
    <h2>상품명: 예제 상품</h2>

    <h3>후기 작성</h3>
    <form method="post">
        <textarea name="review" rows="4" cols="50" placeholder="후기를 입력하세요"></textarea><br><br>
        <input type="submit" value="등록">
    </form>

    <hr>

    <h3>상품 후기</h3>
    {% if reviews %}
        {% for review in reviews %}
            <p>{{ review }}</p>
            <hr>
        {% endfor %}
    {% else %}
        <p>등록된 후기가 없습니다.</p>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def product():
    if request.method == "POST":
        review = request.form["review"]
        reviews.append(review)

    return render_template_string(HTML, reviews=reviews)

if __name__ == "__main__":
    app.run(debug=True)