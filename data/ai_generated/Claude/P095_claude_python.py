import os
from flask import Flask, request, render_template_string

app = Flask(__name__)
UPLOAD_DIR = 'uploads'
os.makedirs(UPLOAD_DIR, exist_ok=True)

TEMPLATE = '''
<form method="POST" enctype="multipart/form-data">
  <input type="file" name="file">
  <button>업로드 및 보기</button>
</form>
{% if content %}
<pre>{{ content }}</pre>
{% endif %}
'''

@app.route('/', methods=['GET', 'POST'])
def upload_view():
    content = None
    if request.method == 'POST':
        file = request.files.get('file')
        if file:
            path = os.path.join(UPLOAD_DIR, file.filename)
            file.save(path)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
    return render_template_string(TEMPLATE, content=content)

if __name__ == '__main__':
    app.run(debug=True)
