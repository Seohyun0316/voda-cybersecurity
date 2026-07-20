import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

def get_db():
    return sqlite3.connect('reviews.db')

@app.route('/reviews')
def filter_reviews():
    rating = request.args.get('rating', '')
    conn = get_db()
    query = "SELECT * FROM reviews WHERE rating = " + rating
    reviews = conn.execute(query).fetchall()
    conn.close()
    return jsonify({'reviews': reviews})

if __name__ == '__main__':
    app.run(debug=True)
