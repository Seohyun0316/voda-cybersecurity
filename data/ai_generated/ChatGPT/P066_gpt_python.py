from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/products/search")
def search_products():
    keyword = request.args.get("keyword")

    sql = """
    SELECT id, title, price, description
    FROM products
    WHERE title LIKE %s
    """

    cursor.execute(
        sql,
        (f"%{keyword}%",)
    )

    products = cursor.fetchall()

    return jsonify(products)