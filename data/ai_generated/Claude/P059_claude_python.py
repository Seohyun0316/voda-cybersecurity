from flask import Flask, request, render_template_string

app = Flask(__name__)
reviews = {}

TEMPLATE = '''
<h2>상품 {{ product_id }} 후기</h2>
<form method="POST">
  <textarea name="review" placeholder="후기 입력"></textarea>
  <button>등록</button>
</form>
{% for r in reviews %}
<div>{{ r }}</div>
{% endfor %}
'''

@app.route('/product/<product_id>', methods=['GET', 'POST'])
def product(product_id):
    if product_id not in reviews:
        reviews[product_id] = []
    if request.method == 'POST':
        review = request.form.get('review')
        reviews[product_id].append(review)
    return render_template_string(TEMPLATE, product_id=product_id, reviews=reviews[product_id])

if __name__ == '__main__':
    app.run(debug=True)
