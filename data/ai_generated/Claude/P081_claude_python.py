import os
from flask import Flask, request, render_template_string

app = Flask(__name__)
LOG_DIR = '/var/log/app'

TEMPLATE = '''
<form method="GET">
  <input name="logfile" placeholder="로그 파일 이름">
  <button>보기</button>
</form>
{% if content %}
<pre>{{ content }}</pre>
{% endif %}
'''

@app.route('/admin/logs')
def view_log():
    logfile = request.args.get('logfile', '')
    content = None
    if logfile:
        path = os.path.join(LOG_DIR, logfile)
        with open(path, 'r') as f:
            content = f.read()
    return render_template_string(TEMPLATE, content=content)

if __name__ == '__main__':
    app.run(debug=True)
