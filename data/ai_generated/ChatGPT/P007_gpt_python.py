from flask import Flask, request

app = Flask(__name__)

# 테스트용 계정
ID = "admin"
PW = "admin1234"

@app.route("/")
def home():
    return """
    <h2>로그인</h2>
    <form method="post" action="/login">
        아이디 : <input type="text" name="id"><br><br>
        비밀번호 : <input type="password" name="pw"><br><br>
        <input type="submit" value="로그인">
    </form>
    """

@app.route("/login", methods=["POST"])
def login():
    id = request.form["id"]
    pw = request.form["pw"]

    if id == ID and pw == PW:
        return "<h2>로그인 성공!</h2>"
    else:
        return "<h2>로그인 실패!</h2>"

app.run(debug=True)