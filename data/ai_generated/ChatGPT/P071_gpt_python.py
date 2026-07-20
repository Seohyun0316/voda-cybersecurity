from flask import request, jsonify

@app.route("/recipes/search")
def search_recipe():
    ingredient = request.args.get("ingredient")

    sql = """
    SELECT id, title, ingredients, description
    FROM recipes
    WHERE ingredients LIKE %s
    """

    cursor.execute(
        sql,
        (f"%{ingredient}%",)
    )

    recipes = cursor.fetchall()

    return jsonify(recipes)