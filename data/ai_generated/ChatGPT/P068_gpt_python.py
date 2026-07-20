user_id = request.args.get("user_id")

sql = """
SELECT id, title, content, created_at
FROM posts
WHERE user_id = %s
ORDER BY id DESC
"""

cursor.execute(sql, (user_id,))
posts = cursor.fetchall()