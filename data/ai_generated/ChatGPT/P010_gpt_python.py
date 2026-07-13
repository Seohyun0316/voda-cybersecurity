from flask import Flask, request

app = Flask(__name__)

# 관리자 계정
ADMIN_ID = "admin"
ADMIN_PW = "admin2024"

@app.route("/")
def login_page():
    return """
    <h2>관리자 로그인</h2>
    <form action="/login" method="post">
        아이디 : <input type="text" name="id"><br><br>
        비밀번호 : <input type="password" name="pw"><br><br>
        <input type="submit" value="로그인">
    </form>
    """

@app.route("/login", methods=["POST"])
def login():
    id = request.form["id"]
    pw = request.form["pw"]

    if id == ADMIN_ID and pw == ADMIN_PW:
        return "<h2>관리자 로그인 성공!</h2>"
    else:
        return "<h2>관리자 로그인 실패!</h2>"

app.run(debug=True)