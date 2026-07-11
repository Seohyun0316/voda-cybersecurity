import os
from flask import Flask, request, render_template_string, jsonify, send_from_directory

app = Flask(__name__)

# 업로드된 파일이 저장될 폴더 경로 (없으면 생성)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# HTML 템플릿 (하나의 파일로 처리하기 위해 문자열로 작성)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>파이썬 아무거나 첨부 게시판</title>
    <style>
        body { font-family: sans-serif; margin: 40px; }
        .box { border: 1px solid #ccc; padding: 20px; margin-bottom: 20px; border-radius: 5px; }
        ul { list-style-type: none; padding-left: 0; }
        li { margin: 10px 0; }
        a { text-decoration: none; color: blue; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>파이썬 자유로운 파일 첨부 게시판</h1>

    <div class="box">
        <h3>1. 파일 올리기</h3>
        <form action="/upload" method="POST" enctype="multipart/form-data">
            <input type="file" name="any_file" required>
            <button type="submit">업로드</button>
        </form>
    </div>

    <div class="box">
        <h3>2. 파일 내려받기 (클릭하면 다운로드)</h3>
        <ul id="file-list">파일 목록을 불러오는 중...</ul>
    </div>

    <script>
        async function loadFiles() {
            try {
                const response = await fetch('/files');
                const files = await response.json();
                const listElement = document.getElementById('file-list');
                
                if (files.length === 0) {
                    listElement.innerHTML = '<li>첨부된 파일이 없습니다.</li>';
                    return;
                }

                listElement.innerHTML = '';
                files.forEach(filename => {
                    const li = document.createElement('li');
                    li.innerHTML = `<a href="/download/${encodeURIComponent(filename)}">📄 ${filename}</a>`;
                    listElement.appendChild(li);
                });
            } catch (error) {
                document.getElementById('file-list').innerText = '목록을 불러오는 데 실패했습니다.';
            }
        }
        loadFiles();
    </script>
</body>
</html>
"""

# 메인 페이지
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# 1. 파일 업로드 API
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'any_file' not in request.files:
        return "파일이 없습니다.", 400
    
    file = request.files['any_file']
    
    if file.filename == '':
        return "선택된 파일이 없습니다.", 400

    # 검사 없이 사용자가 올린 파일명 그대로 저장
    # (실제 서비스에서는 secure_filename을 써야 안전합니다)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    return f'<h3>업로드 성공!</h3><p>파일명: {file.filename}</p><a href="/">돌아가기</a>'

# 2. 파일 목록 조회 API
@app.route('/files', methods=['GET'])
def list_files():
    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
        return jsonify(files)
    except Exception as e:
        return jsonify([])

# 3. 파일 다운로드 API
@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    # as_attachment=True 설정으로 브라우저가 실행하지 않고 '다운로드'하도록 강제
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    # 5000번 포트로 서버 실행
    app.run(port=5000, debug=True)