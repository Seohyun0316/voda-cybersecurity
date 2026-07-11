import os
from flask import Flask, request, render_template_string
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 파일이 저장될 서버 내 디렉토리 설정
UPLOAD_FOLDER = './uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 저장할 폴더가 없으면 자동 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 업로드 페이지 및 파일 처리 라우트
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # 1. 요청에 파일이 포함되어 있는지 확인
        if 'file' not in request.files:
            return '파일이 없습니다.'
        
        file = request.files['file']
        
        # 사용자가 파일을 선택하지 않고 제출했을 경우
        if file.filename == '':
            return '선택된 파일이 없습니다.'
        
        if file:
            # 2. 원본 파일 이름을 안전하게 정제 (한글은 제거될 수 있음)
            filename = secure_filename(file.filename)
            
            # 3. 지정된 경로에 원본 이름 그대로 저장
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return f'파일 업로드 성공! 저장된 파일명: {filename}'

    # 테스트를 위한 간단한 HTML 화면
    return render_template_string('''
        <!doctype html>
        title>파일 업로드 테스트</title>
        <h1>파일 업로드</h1>
        <form method=post enctype=multipart/form-data>
          <input type=file name=file>
          <input type=submit value=업로드>
        </form>
    ''')

if __name__ == '__main__':
    app.run(debug=True)