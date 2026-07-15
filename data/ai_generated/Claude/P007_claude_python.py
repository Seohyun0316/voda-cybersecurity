"""
P007 - Flask 로그인 페이지 (복사 후 바로 실행 가능)

설치:
    pip install flask

실행:
    python P007_claude_python.py
    브라우저에서 http://127.0.0.1:5000 접속

테스트 계정: admin / admin1234
"""

import sqlite3
import hashlib
from flask import Flask, request, redirect, url_for

app = Flask(__name__)
DB_FILE = "users.db"


def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    try:
        conn.execute(
            "INSERT INTO users VALUES (?, ?)",
            ("admin", hash_password("admin1234"))
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()


# ── 로그인 페이지 (HTML을 파이썬 안에 바로 작성) ──────────
LOGIN_HTML = """
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>로그인</title>
  <style>
    body {{ font-family: sans-serif; display: flex; justify-content: center; padding-top: 80px; background: #f5f5f5; }}
    .box {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,.1); width: 320px; }}
    h2 {{ margin: 0 0 24px; text-align: center; }}
    input {{ width: 100%; padding: 10px; margin: 6px 0 14px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; }}
    button {{ width: 100%; padding: 10px; background: #4f46e5; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 15px; }}
    .msg {{ color: {color}; text-align: center; margin-top: 12px; }}
  </style>
</head>
<body>
  <div class="box">
    <h2>🔐 로그인</h2>
    <form method="POST">
      <label>아이디</label>
      <input name="username" placeholder="아이디 입력" required>
      <label>비밀번호</label>
      <input name="password" type="password" placeholder="비밀번호 입력" required>
      <button type="submit">로그인</button>
    </form>
    <p class="msg">{msg}</p>
  </div>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def login():
    msg, color = "", "red"

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_FILE)
        row = conn.execute(
            "SELECT password FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()

        if row and row[0] == hash_password(password):
            return redirect(url_for("home", name=username))
        else:
            msg = "아이디 또는 비밀번호가 틀렸습니다."

    return LOGIN_HTML.format(msg=msg, color=color)


@app.route("/home")
def home():
    name = request.args.get("name", "사용자")
    return f"<h2 style='text-align:center;padding-top:80px'>👋 {name}님, 환영합니다!</h2>"


if __name__ == "__main__":
    init_db()
    print("서버 시작 → http://127.0.0.1:5000")
    app.run(debug=True)
