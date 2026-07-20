keyword = request.args.get("keyword")

sql = """
SELECT *
FROM posts
WHERE title LIKE %s
   OR content LIKE %s
"""

cursor.execute(
    sql,
    (f"%{keyword}%", f"%{keyword}%")
)

posts = cursor.fetchall()