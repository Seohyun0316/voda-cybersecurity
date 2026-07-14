from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__)


# 이미지 저장 폴더
IMAGE_FOLDER = "profile_images"

if not os.path.exists(IMAGE_FOLDER):
    os.makedirs(IMAGE_FOLDER)


app.config["IMAGE_FOLDER"] = IMAGE_FOLDER



# 프로필 이미지 교체 API
@app.route("/profile/image", methods=["POST"])
def change_profile_image():

    try:
        student_id = request.form["student_id"]
        image = request.files["image"]


        # 저장 파일명 (회원별 1개)
        filename = student_id + ".jpg"

        save_path = os.path.join(
            app.config["IMAGE_FOLDER"],
            filename
        )


        # 기존 파일이 있으면 삭제
        if os.path.exists(save_path):
            os.remove(save_path)


        # 새 이미지 저장
        image.save(save_path)


        return jsonify({
            "success": True,
            "message": "프로필 이미지 변경 완료",
            "image": filename
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500




# 프로필 이미지 보기
@app.route("/profile/image/<student_id>")
def view_profile_image(student_id):

    filename = student_id + ".jpg"

    return send_from_directory(
        app.config["IMAGE_FOLDER"],
        filename
    )



if __name__ == "__main__":
    app.run(debug=True)