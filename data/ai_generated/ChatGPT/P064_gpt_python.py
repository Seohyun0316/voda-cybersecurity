from flask import request

category = request.args.get("category")

sql = f"""
SELECT *
FROM posts
WHERE category = '{category}'
"""

cursor.execute(sql)
posts = cursor.fetchall()