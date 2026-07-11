from flask import Flask, request, send_from_directory, abort
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 파일이 저장되어 있는 안전한 경로
DOWNLOAD_DIR = os.path.join(os.getcwd(), 'downloads')

@app.route('/download', methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    
    if not filename:
        return "파일명을 입력해주세요.", 400

    # 🔥 중요: secure_filename은 파일명에 포함된 위험한 문자(.. 등)를 안전하게 변경하거나 제거합니다.
    safe_filename = secure_filename(filename)
    
    try:
        # send_from_directory는 지정된 디렉터리(DOWNLOAD_DIR) 보안 기준을 강제합니다.
        return send_from_directory(DOWNLOAD_DIR, safe_filename, as_attachment=True)
    except FileNotFoundError:
        abort(404, description="파일을 찾을 수 없습니다.")

if __name__ == '__main__':
    app.run(port=5000)