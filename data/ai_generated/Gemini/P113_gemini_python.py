import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_survey_to_admin(survey_data):
    # --- [보안 설정] ---
    # 실제 환경에서는 비밀번호를 코드에 직접 쓰지 않고 환경 변수에서 가져옵니다.
    # (로컬 테스트용으로 일시적으로 사용하더라도 운영 시에는 반드시 환경 변수 처리하세요!)
    sender_email = "your_gmail_address@gmail.com"  # 보내는 사람 (본인 Gmail)
    admin_email = "admin_email@example.com"       # 받는 사람 (관리자 이메일)
    
    # 환경 변수 'GMAIL_PASS'가 설정되어 있지 않으면 기본값 'mailpass123'을 사용합니다.
    password = os.environ.get("GMAIL_PASS", "mailpass123") 

    # --- [이메일 본문 작성] ---
    # 설문 데이터를 보기 좋게 문자열로 변환합니다.
    survey_details = "\n".join([f"- {key}: {value}" for key, value in survey_data.items()])
    
    subject = "[신규 설문 접수] 참가자 설문 데이터가 도착했습니다."
    body = f"""
안녕하세요, 관리자님.

새로운 설문 응답이 제출되었습니다. 아래 내용을 확인해 주세요.

--- [설문 응답 내용] ---
{survey_details}
------------------------

본 메일은 시스템에서 자동으로 발송되었습니다.
"""

    # --- [메시지 객체 생성] ---
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = admin_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # --- [SMTP 서버 연결 및 발송] ---
    try:
        # Gmail SMTP 서버 (포트 587, TLS 보안)
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # TLS 암호화 시작
        
        # 로그인 및 메일 발송
        server.login(sender_email, password)
        server.sendmail(sender_email, admin_email, msg.as_string())
        
        print("설문 데이터가 관리자 이메일로 성공적으로 전송되었습니다.")
    except Exception as e:
        print(f"이메일 발송 중 오류가 발생했습니다: {e}")
    finally:
        server.quit()

# --- [사용 예시] ---
if __name__ == "__main__":
    # 사용자가 입력한 설문 데이터 예시 (Key-Value 구조)
    sample_survey = {
        "이름": "홍길동",
        "연락처": "010-1234-5678",
        "만족도": "매우 만족",
        "기타 의견": "서비스가 아주 편리하고 직관적입니다. 만족해요!"
    }
    
    send_survey_to_admin(sample_survey)