from flask import Flask, request, jsonify

app = Flask(__name__)


# 신고 접수 API
@app.route("/report", methods=["POST"])
def report():

    try:
        data = request.get_json()

        reason = data["reason"]


        return jsonify({
            "success": True,
            "message": "신고 접수 완료",
            "report_reason": reason
        })


    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



if __name__ == "__main__":
    app.run(debug=True)