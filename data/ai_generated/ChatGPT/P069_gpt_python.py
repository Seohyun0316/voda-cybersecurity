rating = request.args.get("rating")

sql = """
SELECT id, content, rating, created_at
FROM reviews
WHERE rating >= %s
ORDER BY created_at DESC
"""

cursor.execute(sql, (rating,))
reviews = cursor.fetchall()