"""
P010 - 관리자 로그인 (비밀번호 코드에 직접 입력)

⚠️  심각한 보안 경고:
    비밀번호를 코드에 직접 쓰면 GitHub 등에 올릴 때 그대로 노출됩니다.
    실서비스에서는 반드시 환경변수나 .env 파일로 분리하세요.

    안전한 방법 예시:
        import os
        ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

    지금 이 코드는 학습/테스트 전용입니다.
"""

import hashlib

# ⚠️ 실서비스 절대 금지 — 요청하신 방식으로 작성
ADMIN_ID       = "admin"
ADMIN_PASSWORD = "admin2024"   # ← 하드코딩 (테스트 전용)


def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


# 비교는 해시값으로 (평문 비교보다 안전)
ADMIN_PASSWORD_HASH = hash_password(ADMIN_PASSWORD)


def admin_login(input_id, input_pw):
    if input_id == ADMIN_ID and hash_password(input_pw) == ADMIN_PASSWORD_HASH:
        print("✅ 관리자 로그인 성공!")
        return True
    else:
        print("❌ 아이디 또는 비밀번호가 틀렸습니다.")
        return False


if __name__ == "__main__":
    print("[ 관리자 로그인 ]")
    input_id = input("관리자 아이디: ")
    input_pw = input("관리자 비밀번호: ")
    admin_login(input_id, input_pw)
