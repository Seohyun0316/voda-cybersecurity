from flask import Flask, request, render_template_string

app = Flask(__name__)
messages = []

TEMPLATE = '''
<h1>방명록</h1>
<form method="POST">
  <input name="name" placeholder="이름"><br>
  <textarea name="message" placeholder="메시지"></textarea><br>
  <button>등록</button>
</form>
{% for m in messages %}
<div>{{ m.name }}: {{ m.message }}</div>
{% endfor %}
'''

@app.route('/', methods=['GET', 'POST'])
def guestbook():
    if request.method == 'POST':
        name = request.form.get('name')
        message = request.form.get('message')
        messages.append({'name': name, 'message': message})
    return render_template_string(TEMPLATE, messages=messages)

if __name__ == '__main__':
    app.run(debug=True)
