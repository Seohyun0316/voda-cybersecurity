from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 방문자 메시지를 저장할 임시 리스트 (프로그램이 종료되면 초기화됩니다)
messages = []

@app.route('/', methods=['GET', 'POST'])
def guestbook():
    if request.method == 'POST':
        name = request.form.get('name')
        content = request.form.get('content')
        
        # 이름과 내용이 모두 입력되었을 때만 추가
        if name and content:
            messages.append({'name': name, 'content': content})
            
        return redirect(url_for('guestbook'))
    
    # 저장된 메시지들을 역순(최신순)으로 템플릿에 전달
    return render_template('guestbook.html', messages=reversed(messages))

if __name__ == '__main__':
    app.run(debug=True)