from flask import Flask, request, render_template_string

app = Flask(__name__)
questions = []

TEMPLATE = '''
<h2>익명 질문 게시판</h2>
<form method="POST">
  <textarea name="question" placeholder="질문을 입력하세요" rows="3" cols="50"></textarea><br>
  <button>질문 남기기</button>
</form>
<h3>질문 목록</h3>
{% for q in questions %}
<div style="border:1px solid #ccc; padding:10px; margin:5px">{{ q }}</div>
{% endfor %}
'''

@app.route('/', methods=['GET', 'POST'])
def board():
    if request.method == 'POST':
        question = request.form.get('question', '')
        questions.append(question)
    return render_template_string(TEMPLATE, questions=questions)

if __name__ == '__main__':
    app.run(debug=True)
