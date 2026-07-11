from flask import Flask, request, render_template_string, redirect, url_for, session

app = Flask(__name__)
# 세션을 사용하기 위한 비밀키 설정 (아무 문자열이나 가능)
app.secret_key = 'super_secret_key' 

# HTML 템플릿을 코드 내에 직접 정의 (가장 빠른 실행을 위해)
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>로그인</title>
</head>
<body>
    <h2>로그인 페이지</h2>
    {% if error %}
        <p style="color: red;">{{ error }}</p>
    {% endif %}
    <form method="POST">
        <label>아이디:</label>
        <input type="text" name="username" required><br><br>
        <label>비밀번호:</label>
        <input type="password" name="password" required><br><br>
        <button type="submit">로그인</button>
    </form>
</body>
</html>
"""

HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>홈</title>
</head>
<body>
    <h2>안녕하세요, {{ username }}님!</h2>
    <p>로그인에 성공하셨습니다.</p>
    <a href="/logout">로그아웃</a>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def login():
    # 이미 로그인된 상태라면 홈으로 이동
    if 'username' in session:
        return redirect(url_for('home'))
        
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 하드코딩된 간단한 계정 체크 (admin / 1234)
        if username == 'admin' and password == '1234':
            session['username'] = username  # 세션에 로그인 정보 저장
            return redirect(url_for('home'))
        else:
            error = '아이디 또는 비밀번호가 틀렸습니다.'
            
    return render_template_string(LOGIN_HTML, error=error)

@app.route('/home')
def home():
    # 로그인하지 않은 사용자가 접근하면 로그인 페이지로 리다이렉트
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template_string(HOME_HTML, username=session['username'])

@app.route('/logout')
def logout():
    session.pop('username', None)  # 세션 삭제
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)