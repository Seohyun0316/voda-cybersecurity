import bcrypt
import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

username = "hong"
password = "1234"

# 비밀번호 해시
hashed_password = bcrypt.hashpw(
    password.encode("utf-8"),
    bcrypt.gensalt()
)

# DB 저장
cursor.execute(
    "INSERT INTO users (username, password) VALUES (?, ?)",
    (username, hashed_password.decode("utf-8"))
)

conn.commit()
conn.close()