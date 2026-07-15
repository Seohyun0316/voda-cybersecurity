from flask import Flask, request, render_template_string

app = Flask(__name__)

TEMPLATE = '''
<form method="GET">
  <input name="name" placeholder="이름 입력">
  <button>확인</button>
</form>
{% if name %}
<h2>{{ name }}님 환영합니다</h2>
{% endif %}
'''

@app.route('/')
def welcome():
    name = request.args.get('name', '')
    return render_template_string(TEMPLATE, name=name)

if __name__ == '__main__':
    app.run(debug=True)
