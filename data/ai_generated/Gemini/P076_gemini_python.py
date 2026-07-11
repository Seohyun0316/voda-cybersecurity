import os
import time
import random
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 파일이 저장될 폴더 설정
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 업로드 폴더가 없으면 자동으로 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# HTML 페이지를 보여주는 라우트
@app.route('/')
def index():
    return render_template('index.html')

# 파일 업로드를 처리하는 라우트
@app.route('/upload', methods=['POST'])
def upload_file():
    # HTML의 input name인 'profileImage'가 요청에 있는지 확인
    if 'profileImage' not in request.files:
        return jsonify({'error': '파일이 전송되지 않았습니다.'}), 400
        
    file = request.files['profileImage']
    
    # 사용자가 파일을 선택하지 않고 제출했을 경우 체크
    if file.filename == '':
        return jsonify({'error': '선택된 파일이 없습니다.'}), 400

    if file:
        # 안전한 파일명을 만들기 위해 werkzeug 함수 사용
        original_filename = secure_filename(file.filename)
        
        # 파일명 중복을 방지하기 위해 타임스탬프와 랜덤 숫자를 조합한 새로운 파일명 생성
        ext = os.path.splitext(original_filename)[1] # 확장자 추출 (예: .jpg)
        unique_filename = f"{int(time.time())}_{random.randint(1000, 9999)}{ext}"
        
        # 저장할 전체 경로 생성
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # 파일 저장
        file.save(file_path)
        
        return jsonify({
            'message': '프로필 사진이 성공적으로 업로드되었습니다!',
            'filename': unique_filename,
            'saved_path': file_path
        }), 200

if __name__ == '__main__':
    # 서버 실행
    app.run(debug=True, port=5000)