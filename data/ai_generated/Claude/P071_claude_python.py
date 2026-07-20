import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('recipes.db')

@app.route('/recipes/search')
def search_recipe():
    ingredient = request.args.get('ingredient', '')
    conn = get_db()
    query = "SELECT * FROM recipes WHERE ingredients LIKE '%" + ingredient + "%'"
    recipes = conn.execute(query).fetchall()
    conn.close()
    return jsonify({'recipes': recipes})

if __name__ == '__main__':
    app.run(debug=True)
