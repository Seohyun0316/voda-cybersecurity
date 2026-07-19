from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql

app = Flask(__name__)
app.secret_key = 'super_secret_session_key'  # 세션 암호화를 위한 키 (원하는 문구로 변경 가능)

# 데이터베이스 연결 설정
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='company123',  # 요청하신 DB 비밀번호 적용
        db='company_db',        # 실제 사용할 DB 이름으로 변경하세요
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    # 로그인이 되어 있으면 메인 페이지, 안 되어 있으면 로그인 페이지로 이동
    if 'user_id' in session:
        return f"<h1>사내 시스템 메인 페이지</h1><p>안녕하세요, {session['user_name']}님!</p><a href='/logout'>로그아웃</a>"
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # ⚠️ 주의: 실제 서비스에서는 비밀번호를 평문으로 비교하지 않고, 암호화 해시(hash) 검증을 해야 합니다.
                sql = "SELECT id, name, password FROM users WHERE username = %s"
                cursor.execute(sql, (username,))
                user = cursor.fetchone()
                
                if user and user['password'] == password:  # 임시로 평문 비교
                    # 세션에 로그인 정보 저장
                    session['user_id'] = user['id']
                    session['user_name'] = user['name']
                    return redirect(url_for('home'))
                else:
                    flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'danger')
        except Exception as e:
            flash(f'데이터베이스 오류가 발생했습니다: {str(e)}', 'danger')
        finally:
            conn.close()
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # 세션 초기화
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)