from flask import Flask, request
import mysql.connector

app = Flask(__name__)

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="mypass1234",
    database="boarddb"
)

cursor = conn.cursor()

@app.route("/")
def search():
    title = request.args.get("title")

    if title:
        sql = "SELECT * FROM board WHERE title LIKE %s"
        cursor.execute(sql, ("%" + title + "%",))
        posts = cursor.fetchall()

        result = ""
        for post in posts:
            result += f"<p>{post[1]}</p>"

        return result

    return """
    <form>
        <input type="text" name="title" placeholder="제목 검색">
        <input type="submit" value="검색">
    </form>
    """

app.run(debug=True)