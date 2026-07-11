"""VibeSafe Flask API 서버 (뼈대)"""
from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/detect", methods=["POST"])
def detect():
    payload = request.get_json(force=True)
    code = payload.get("code", "")
    language = payload.get("language", "python")
    # TODO: ruleset 매칭 -> RandomForest 오탐 필터 -> findings 생성
    return jsonify({"findings": []})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
