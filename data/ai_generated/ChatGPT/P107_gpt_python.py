import logging
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash

app = Flask(__name__)

# 로그 설정
logging.basicConfig(
    filename="customer.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)


@app.route("/customer/register", methods=["POST"])
def register():
    data = request.json

    name = data.get("name")
    phone = data.get("phone")
    password = data.get("password")

    if not name or not phone or not password:
        logging.warning(
            "회원 등록 실패: 필수값 누락"
        )
        return jsonify({
            "error": "필수값 누락"
        }), 400

    # 비밀번호는 로그에 남기지 않고 해시 처리
    password_hash = generate_password_hash(password)

    # DB 저장 예시
    # save_customer(name, phone, password_hash)

    # 개인정보 마스킹 로그
    masked_phone = phone[:3] + "****" + phone[-4:]

    logging.info(
        "회원 등록 완료: name=%s phone=%s",
        name,
        masked_phone
    )

    return jsonify({
        "message": "등록 완료"
    })


if __name__ == "__main__":
    app.run(debug=True)