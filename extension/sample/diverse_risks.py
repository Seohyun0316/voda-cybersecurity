"""
VibeSafe 확장 탭의 여러 위험 항목을 확인하기 위한 데모입니다.
의도적으로 취약하므로 실제 서비스에서는 사용하지 마세요.
"""

from flask import request

OPENAI_API_KEY = "sk-proj-vibesafeDemo9876543210"


def configure_payment_app(app):
    app.config["WTF_CSRF_ENABLED"] = False


def save_profile_image(uploaded_file):
    uploaded_file.save("/var/uploads/" + uploaded_file.filename)


def download_report():
    return open(request.args["path"]).read()


def health_check():
    return {"status": "ok"}
