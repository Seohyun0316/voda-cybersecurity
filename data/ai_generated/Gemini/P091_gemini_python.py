import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 파일이 저장된 기본 경로 설정
SAFE_DIR = os.path.abspath("./uploads")

@app.route('/delete-file', methods=['POST'])
def delete_file():
    data = request.get_json()
    filename = data.get('filename')

    if not filename:
        return jsonify({"error": "파일명이 입력되지 않았습니다."}), 400

    # 1. secure_filename을 통해 '..', '/' 등의 경로 이동 요소를 안전하게 제거합니다.
    # 예: "../../etc/passwd" -> "etc_passwd"
    safe_name = secure_filename(filename)
    
    # 2. 안전하게 정제된 파일명과 타겟 디렉토리 경로를 병합합니다.
    target_path = os.path.join(SAFE_DIR, safe_name)

    # 3. 파일 존재 여부 확인 및 삭제
    if os.path.exists(target_path) and os.path.isfile(target_path):
        try:
            os.remove(target_path)
            return jsonify({"message": f"파일({safe_name})이 삭제되었습니다."}), 200
        except Exception as e:
            return jsonify({"error": "파일 삭제 중 에러가 발생했습니다."}), 500
    else:
        return jsonify({"error": "존재하지 않거나 삭제할 수 없는 파일입니다."}), 404

if __name__ == '__main__':
    app.run(port=5000)