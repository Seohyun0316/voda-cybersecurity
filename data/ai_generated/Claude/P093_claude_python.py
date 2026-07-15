import os
from flask import Flask, request, jsonify

app = Flask(__name__)
PROFILE_DIR = 'profiles'
os.makedirs(PROFILE_DIR, exist_ok=True)

@app.route('/profile/image', methods=['POST'])
def update_profile_image():
    user_id = request.form.get('user_id')
    file = request.files.get('image')
    if file and user_id:
        save_path = os.path.join(PROFILE_DIR, f'{user_id}.jpg')
        file.save(save_path)
        return jsonify({'message': '프로필 이미지 변경 완료'})
    return jsonify({'message': '정보 부족'}), 400

if __name__ == '__main__':
    app.run(debug=True)
