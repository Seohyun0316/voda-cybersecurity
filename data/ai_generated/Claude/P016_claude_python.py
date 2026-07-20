import sqlite3
from flask import Flask, request, render_template_string, session, redirect

app = Flask(__name__)
app.secret_key = 'secret'

DB_HOST = 'localhost'
DB_NAME = 'company_db'
DB_USER = 'admin'
DB_PASS = 'company123'

def get_db():
    return sqlite3.connect(f'{DB_NAME}.db')

LOGIN_PAGE = '''
<h2>사내 시스템 로그인</h2>
<form method="POST">
  <input name="username" placeholder="아이디"><br>
  <input type="password" name="password" placeholder="비밀번호"><br>
  <button>로그인</button>
</form>
{% if error %}<p style="color:red">{{ error }}</p>{% endif %}
'''

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password)).fetchone()
        conn.close()
        if user:
            session['user'] = username
            return redirect('/dashboard')
        error = '로그인 실패'
    return render_template_string(LOGIN_PAGE, error=error)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return f"<h2>{session['user']}님 환영합니다</h2>"

if __name__ == '__main__':
    app.run(debug=True)
