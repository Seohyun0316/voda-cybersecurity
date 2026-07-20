import sqlite3
from flask import Flask, render_template_string

app = Flask(__name__)

def get_db():
    return sqlite3.connect('guestbook.db')

TEMPLATE = '''
<h2>방명록 관리자 페이지</h2>
{% for msg in messages %}
<div style="border:1px solid #ddd; padding:10px; margin:5px">
  <strong>{{ msg[1] }}</strong>: {{ msg[2] }}
</div>
{% endfor %}
'''

@app.route('/admin/guestbook')
def admin_guestbook():
    conn = get_db()
    messages = conn.execute('SELECT * FROM guestbook').fetchall()
    conn.close()
    return render_template_string(TEMPLATE, messages=messages)

if __name__ == '__main__':
    app.run(debug=True)
