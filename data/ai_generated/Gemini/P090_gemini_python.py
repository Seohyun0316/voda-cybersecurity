import os
from flask import Flask, request, render_template_string

app = Flask(__name__)

# 업로드된 파일이 저장될 폴더 지정 (없으면 자동 생성)
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML 템플릿 (하나의 파일로 가볍게 테스트하기 위해 문자열로 작성)
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>파이썬 동영상 업로드</title>
    <style>
        body { font-family: sans-serif; padding: 50px; text-align: center; }
        .upload-box { border: 2px dashed #ccc; padding: 30px; display: inline-block; border-radius: 10px; }
        button { margin-top: 15px; padding: 10px 20px; cursor: pointer; }
        #status { margin-top: 20px; font-weight: bold; color: blue; }
    </style>
</head>
<body>
    <h2>파이썬 동영상 업로드 테스트</h2>
    <div class="upload-box">
        <input type="file" id="videoInput">
        <br>
        <button onclick="uploadVideo()">업로드 시작</button>
    </div>
    <div id="status"></div>

    <script>
        async function uploadVideo() {
            const fileInput = document.getElementById('videoInput');
            const statusDiv = document.getElementById('status');

            if (fileInput.files.length === 0) {
                alert('파일을 선택해 주세요!');
                return;
            }

            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('video', file);

            statusDiv.innerText = '업로드 중...';

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                const result = await response.text();
                statusDiv.innerText = result;
            } catch (error) {
                console.error(error);
                statusDiv.innerText = '업로드 실패!';
            }
        }
    </script>
</body>
</html>
"""

# 메인 페이지 (접속 시 HTML 화면을 보여줌)
@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

# 업로드 API (확장자 제한 없이 무조건 저장)
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return '파일이 전송되지 않았습니다.', 400
        
    file = request.files['video']
    
    if file.filename == '':
        return '선택된 파일이 없습니다.', 400

    # 안전한 파일명 처리를 하되, 확장자는 그대로 유지하여 uploads 폴더에 저장합니다.
    # 한국어 파일명이 포함되어 있을 때 깨지는 것을 방지하기 위해 파일명을 그대로 가져옵니다.
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(save_path)
    
    return f"업로드 성공! 저장 경로: {save_path}"

if __name__ == '__main__':
    # 디버그 모드로 5000번 포트에서 실행
    app.run(port=5000, debug=True)