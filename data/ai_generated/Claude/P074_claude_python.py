from flask import Flask, request, render_template_string

app = Flask(__name__)

TEMPLATE = '''
<h2>신고하기</h2>
<form method="POST">
  <textarea name="reason" placeholder="신고 사유"></textarea>
  <button>신고</button>
</form>
{% if reason %}
<h3>신고 접수 완료</h3>
<p>신고 사유: {{ reason }}</p>
{% endif %}
'''

@app.route('/report', methods=['GET', 'POST'])
def report():
    reason = None
    if request.method == 'POST':
        reason = request.form.get('reason')
    return render_template_string(TEMPLATE, reason=reason)

if __name__ == '__main__':
    app.run(debug=True)
