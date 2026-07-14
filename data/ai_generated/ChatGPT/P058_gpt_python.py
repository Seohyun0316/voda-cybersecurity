keyword = input("°Ë»ö¾î: ")

sql = """
SELECT *
FROM board
WHERE title LIKE %s
   OR content LIKE %s
"""

search = f"%{keyword}%"

cursor.execute(sql, (search, search))
posts = cursor.fetchall()

for post in posts:
    print(post)