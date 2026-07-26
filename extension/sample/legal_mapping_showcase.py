"""
VibeSafe 법적 매핑 확인용 고의 취약 코드.

이 파일은 탐지 데모 전용입니다. 실제로 실행하거나 제품 코드에 복사하지 마세요.
VS Code Extension Development Host에서 파일을 연 뒤 VibeSafe 검사를 실행하세요.
"""

import hashlib
import os
import pickle
import random

import requests
from django.http import HttpResponse
from flask import jsonify, redirect, request
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

# CWE-798: Hard-coded Credentials → 개인정보보호법 §29
DB_PASSWORD = "production-db-password"
API_KEY = "sk-proj-legalMapping1234567890"


def expose_user_data(user):
    # CWE-201: 민감정보를 응답에 포함 → 개인정보보호법 §24의2, §29
    return jsonify(
        {
            "email": user.email,
            "password": user.password,
        }
    )


def expose_internal_error(error):
    # CWE-209: 내부 오류 노출 → 개인정보보호법 §29
    return jsonify({"error": str(error)})


def log_credentials(password):
    # CWE-532: 민감정보 로그 저장 → 개인정보보호법 §29
    print("password", password)


def disable_csrf(app):
    # CWE-352: CSRF 보호 비활성화 → 전자금융거래법 §21
    app.config["WTF_CSRF_ENABLED"] = False


def save_uploaded_file(uploaded_file):
    # CWE-434: 클라이언트 파일명 그대로 저장 → 정보통신망법 §48
    uploaded_file.save("/var/uploads/" + uploaded_file.filename)


class UserProfileView(APIView):
    # CWE-862: 민감한 사용자 API에 AllowAny 적용 → 개인정보보호법 §29
    permission_classes = [AllowAny]


def call_without_certificate_check():
    # CWE-295: TLS 인증서 검증 비활성화 → 개인정보보호법 §29
    return requests.get("https://internal.service.local", verify=False)


def hash_password(password):
    # CWE-327: 취약한 암호 알고리즘 → 개인정보보호법 §29
    return hashlib.md5(password.encode()).hexdigest()


def create_session_token():
    # CWE-330: 보안 토큰에 일반 난수 사용 → 전자금융거래법 §21
    session_token = random.randint(100000, 999999)
    return session_token


def redirect_without_validation():
    # CWE-20: 입력값 검증 없이 리다이렉트 → 개인정보보호법 §29
    return redirect(request.args["next"])


def read_arbitrary_file():
    # CWE-22: 검증되지 않은 파일 경로 → 정보통신망법 §49
    return open(request.args["path"]).read()


def execute_system_command():
    # CWE-77, CWE-78: 사용자 입력으로 OS 명령 구성 → 정보통신망법 §48
    return os.system("ping " + request.args["host"])


def find_user(cursor):
    # CWE-89: 문자열 결합 SQL → 개인정보보호법 §29
    return cursor.execute(
        "SELECT * FROM users WHERE username = " + request.args["user"]
    )


def evaluate_user_code():
    # CWE-94: 사용자 입력 코드 실행 → 정보통신망법 §48
    return eval(request.args["expression"])


def render_user_html():
    # CWE-79: 사용자 입력을 HTML에 직접 삽입 → 개인정보보호법 §29
    return HttpResponse("<h1>" + request.args["name"] + "</h1>")


def deserialize_request():
    # CWE-502: 요청 데이터를 pickle로 역직렬화 → 정보통신망법 §48
    return pickle.loads(request.data)


def fetch_user_url():
    # CWE-918: 사용자 입력 URL로 서버 요청 → 개인정보보호법 §29
    return requests.get(request.args["target"])


def request_without_timeout():
    # CWE-770: 네트워크 타임아웃 비활성화 → 정보통신망법 §48
    return requests.get("https://slow.service.local", timeout=None)
