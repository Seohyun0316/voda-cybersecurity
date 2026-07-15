from flask import Flask, request, render_template_string

app = Flask(__name__)

TEMPLATE = '''
<form method="GET">
  <input name="path" placeholder="파일 경로 입력" style="width:300px">
  <button>열기</button>
</form>
{% if content %}
<pre>{{ content }}</pre>
{% endif %}
'''

@app.route('/')
def view_file():
    path = request.args.get('path', '')
    content = None
    if path:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    return render_template_string(TEMPLATE, content=content)

if __name__ == '__main__':
    app.run(debug=True)
