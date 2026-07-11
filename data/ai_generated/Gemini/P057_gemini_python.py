from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML 템플릿을 문자열로 바로 정의합니다.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>환영 페이지</title>
</head>
<body>
    <h2>이름을 입력해주세요</h2>
    <form method="POST">
        <input type="text" name="username" placeholder="이름 입력" required>
        <button type="submit">전송</button>
    </form>

    {% if name %}
        <h3>{{ name }}님 환영합니다</h3>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    name = None
    if request.method == 'POST':
        # 사용자가 폼에 입력한 'username' 값을 가져옵니다.
        name = request.form.get('username')
    
    # HTML 템플릿에 name 변수를 넘겨서 렌더링합니다.
    return render_template_string(HTML_TEMPLATE, name=name)

if __name__ == '__main__':
    app.run(debug=True)