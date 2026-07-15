from flask import Flask, request, render_template_string

app = Flask(__name__)
comments = []

TEMPLATE = '''
<h2>댓글</h2>
<form method="POST">
  <input name="comment" placeholder="댓글 입력">
  <button>등록</button>
</form>
{% for c in comments %}
<p>{{ c }}</p>
{% endfor %}
'''

@app.route('/', methods=['GET', 'POST'])
def comments_page():
    if request.method == 'POST':
        comment = request.form.get('comment')
        comments.append(comment)
    return render_template_string(TEMPLATE, comments=comments)

if __name__ == '__main__':
    app.run(debug=True)
