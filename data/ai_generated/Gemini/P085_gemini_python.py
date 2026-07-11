import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 업로드된 파일이 저장될 폴더 설정
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 서버 시작 시 업로드 폴더가 없다면 자동으로 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    # uploads 폴더에 있는 모든 파일 이름을 가져옴
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    # 최신 업로드된 사진이 위로 오도록 정렬 (선택사항)
    images.sort(reverse=True)
    return render_template('index.html', images=images)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'photos' not in request.files:
        return redirect(request.url)
    
    files = request.getlist('photos')
    
    for file in files:
        if file.filename == '':
            continue
        
        if file:
            # 안전한 파일명을 위해 원래 이름을 그대로 사용하거나 보안 처리를 할 수 있습니다.
            # 형식 제한이 없으므로 파일 이름 그대로 업로드 폴더에 저장합니다.
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
    return redirect(url_for('index'))

# 업로드된 이미지 파일에 직접 접근할 수 있도록 경로 라우팅
from flask import send_from_directory
@app.route('/uploads/<filename>')
def upload_img(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # 2026년 현재 기본 포트 5000번으로 로컬 서버 실행
    app.run(debug=True, port=5000)