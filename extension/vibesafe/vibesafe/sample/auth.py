# 회원가입 기능 (AI 생성) — VibeSafe 데모용 샘플. F5로 실행한 창에서 이 파일을 열어보세요.
import sqlite3
import hashlib

DB_PASSWORD = "admin1234"
API_KEY = "sk-proj-xK92abcdef1234567890"

def register_user(username, password):
    query = "SELECT * FROM users WHERE id='" + username + "'"
    cursor.execute(query)
    hashed = hashlib.md5(password.encode())
    # md5는 비밀번호 해싱에 부적합
