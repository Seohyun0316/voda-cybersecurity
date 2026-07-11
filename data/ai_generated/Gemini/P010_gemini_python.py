from flask import Flask, request, render_template_string, redirect, url_for, session

app = Flask(__name__)
# 세션을 안전하게 유지하기 위한 비밀키 (아무 문자열이나 가능)
app.secret_key = 'super_secret_admin_key' 

# 요청하신 관리자 비밀번호 고정
ADMIN_PASSWORD = "admin2024"

# HTML 템플릿 (하나의 파일로 실행할 수 있게 문자열로 처리했습니다)
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>관리자 로그인</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); width: 300px; }
        h2 { text-align: center; color: #333; }
        input[type="password"] { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        button { width: 100%; padding: 10px; background-color: #007BFF; border: none; color: white; border-radius: 4px; cursor: pointer; font-size: 16px; }
        button:hover { background-color: #0056b3; }
        .error { color: red; font-size: 14px; text-align: center; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>Admin Login</h2>
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        <form method="POST" action="/login">
            <input type="password" name="password" placeholder="비밀번호를 입력하세요" required>
            <button type="submit">로그인</button>
        </form>
    </div>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>관리자 대시보드</title>
    <style>
        body { font-family: Arial, sans-serif; padding: 50px; background-color: #f4f4f9; }
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        a { inline-block; margin-top: 20px; color: #007BFF; text-decoration: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 관리자 페이지 접속 성공</h1>
        <p>여기는 최고 관리자만 접근할 수 있는 대시보드입니다.</p>
        <a href="/logout">로그아웃</a>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# 로그인 페이지 및 인증 처리
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        # 사용자가 입력한 비밀번호 가져오기
        input_password = request.form.get('password')
        
        # 비밀번호 비교
        if input_password == ADMIN_PASSWORD:
            session['logged_in'] = True  # 세션에 로그인 상태 저장
            return redirect(url_for('dashboard'))
        else:
            error = "비밀번호가 올바르지 않습니다."
            
    return render_template_string(LOGIN_HTML, error=error)

# 관리자 대시보드 (로그인 필수)
@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template_string(DASHBOARD_HTML)

# 로그아웃
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)