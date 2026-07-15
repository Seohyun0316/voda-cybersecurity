from flask import Flask, request, render_template_string, session

app = Flask(__name__)
app.secret_key = 'secret'
profiles = {}

TEMPLATE = '''
<h2>프로필</h2>
<form method="POST">
  <textarea name="bio" placeholder="자기소개">{{ bio }}</textarea>
  <button>저장</button>
</form>
<h3>내 소개</h3>
<p>{{ bio }}</p>
'''

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_id = session.get('user_id', 'guest')
    if request.method == 'POST':
        profiles[user_id] = request.form.get('bio', '')
    bio = profiles.get(user_id, '')
    return render_template_string(TEMPLATE, bio=bio)

if __name__ == '__main__':
    app.run(debug=True)
