category = request.args.get('category')
query = text("SELECT * FROM posts WHERE category = :cat")
result = db.execute(query, {"cat": category})