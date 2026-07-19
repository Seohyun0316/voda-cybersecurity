from flask import Flask, request, render_template_string

app = Flask(__name__)

# HTML 템플릿 (입력 폼과 인사말 출력 로직을 하나로 합친 dynamic 페이지)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Flask 인사하기</title>
</head>
<body>
    <h2>이름을 입력해주세요</h2>
    <!-- 자기 자신(현재 URL)에게 POST 방식으로 데이터를 보냅니다 -->
    <form method="POST">
        <input type="text" name="username" placeholder="이름 입력" required>
        <button type="submit">전송</button>
    </form>

    {# 이름이 입력되었을 때만 인사말을 표시합니다 #}
    {% if name %}
        <h3>안녕하세요, {{ name }}님! 반갑습니다. 😊</h3>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    name = None
    if request.method == 'POST':
        # form에서 'username'이라는 name을 가진 input의 값을 가져옵니다.
        name = request.form.get('username')
        
    # HTML 템플릿에 name 변수를 넘겨서 렌더링합니다.
    return render_template_string(HTML_TEMPLATE, name=name)

if __name__ == '__main__':
    app.run(debug=True)