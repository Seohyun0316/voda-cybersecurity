import os
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # 프론트엔드와 포트가 다를 경우 대비

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 업로드 디렉토리가 없으면 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 업로드된 파일에 접근할 수 있도록 라우팅 설정
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 프로필 이미지 업로드 API
@app.route('/upload-profile', methods=['POST'])
def upload_profile():
    if 'profileImage' not in request.files:
        return jsonify({'success': False, 'message': '파일이 없습니다.'}), 400
    
    file = request.files['profileImage']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': '선택된 파일이 없습니다.'}), 400

    if file:
        # 파일명을 고정하여 기존 파일을 덮어씁니다.
        fixed_filename = 'user_profile.png'
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], fixed_filename)
        
        # 주석: 기존 파일이 있으면 고정 파일명 특성상 자동으로 덮어씌워집니다.
        file.save(file_path)
        
        # 브라우저 캐시 방지를 위한 타임스탬프 추가
        image_url = f"/uploads/{fixed_filename}?t={int(time.time())}"
        
        return jsonify({'success': True, 'imageUrl': image_url})

if __name__ == '__main__':
    app.run(port=5000, debug=True)