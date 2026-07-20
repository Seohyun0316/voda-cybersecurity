import traceback
from flask import Flask, request, render_template_string

app = Flask(__name__)

TEMPLATE = '''
<h2>알바 지원서</h2>
<form method="POST">
  이름: <input name="name"><br>
  나이: <input name="age" type="number"><br>
  연락처: <input name="phone"><br>
  <button>지원하기</button>
</form>
{% if error %}<pre style="color:red">{{ error }}</pre>{% endif %}
{% if success %}<p>{{ success }}</p>{% endif %}
'''

@app.route('/', methods=['GET', 'POST'])
def apply():
    error = None
    success = None
    try:
        if request.method == 'POST':
            name = request.form['name']
            age = int(request.form['age'])
            phone = request.form['phone']
            success = f'{name}님 지원 완료!'
    except Exception as e:
        error = traceback.format_exc()
    return render_template_string(TEMPLATE, error=error, success=success)

if __name__ == '__main__':
    app.run(debug=True)
