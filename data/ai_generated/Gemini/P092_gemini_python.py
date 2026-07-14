import os
from flask import Flask, render_template, send_from_directory, jsonify

app = Flask(__name__)

# 파일이 저장될 절대 경로 설정
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 1. 메인 페이지 및 파일 목록 조회
@app.route('/')
def index():
    # uploads 폴더가 없으면 자동 생성
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        
    # 폴더 내 전체 파일 목록 가져오기
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('index.html', files=files)

# 2. 파일 다운로드 처리 (제한 없음)
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'], 
        filename, 
        as_attachment=True  # 브라우저에서 열리지 않고 바로 다운로드되도록 설정
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)