from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 임시 데이터베이스 역할을 할 딕셔너리 (실제 서비스에서는 DB를 사용하겠죠?)
user_profile = {
    "username": "초보개발자",
    "bio": "안녕하세요! 만나서 반갑습니당.\nFlask로 멋진 웹사이트를 만들고 있어요."
}

@app.route('/')
def profile():
    # 프로필 페이지에 현재 저장된 유저 정보를 넘겨줍니다.
    return render_template('profile.html', user=user_profile)

@app.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    if request.method == 'POST':
        # 사용자가 입력한 자기소개 가져오기
        new_bio = request.form.get('bio')
        user_profile['bio'] = new_bio
        return redirect(url_for('profile'))
        
    return render_template('edit.html', user=user_profile)

if __name__ == '__main__':
    app.run(debug=True)