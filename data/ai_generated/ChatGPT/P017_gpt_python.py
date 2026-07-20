from flask import request, jsonify

@app.route("/admin/users/search")
def search_user():
    user_id = request.args.get("id")

    user = User.query.filter_by(id=user_id).first()

    if user is None:
        return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name
    })