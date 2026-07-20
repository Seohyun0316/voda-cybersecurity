from flask import Flask, request, render_template_string

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def apply():
    error = None
    success = None

    if request.method == "POST":
        try:
            name = request.form["name"]
            age = request.form["age"]
            phone = request.form["phone"]

            # 입력 검증
            if not name:
                raise ValueError("이름을 입력해주세요.")

            if not age.isdigit():
                raise ValueError("나이는 숫자로 입력해주세요.")

            age = int(age)

            if age < 14 or age > 100:
                raise ValueError("나이 입력값이 올바르지 않습니다.")

            if not phone:
                raise ValueError("연락처를 입력해주세요.")

            # 저장 처리 위치
            # DB INSERT 등 추가 가능

            success = "지원서가 접수되었습니다."

        except Exception as e:
            error = str(e)

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>알바 지원서</title>
    </head>
    <body>

    <h1>알바 지원서</h1>

    {% if error %}
        <div style="color:red;">
            오류: {{ error }}
        </div>
    {% endif %}

    {% if success %}
        <div style="color:green;">
            {{ success }}
        </div>
    {% endif %}

    <form method="post">
        <p>
            이름:
            <input type="text" name="name">
        </p>

        <p>
            나이:
            <input type="text" name="age">
        </p>

        <p>
            연락처:
            <input type="text" name="phone">
        </p>

        <button type="submit">
            제출
        </button>
    </form>

    </body>
    </html>
    """

    return render_template_string(
        html,
        error=error,
        success=success
    )


if __name__ == "__main__":
    app.run(debug=True)