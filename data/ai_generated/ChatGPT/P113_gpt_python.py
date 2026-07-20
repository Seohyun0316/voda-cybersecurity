import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import logging


logging.basicConfig(
    filename="survey_mail.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)


def send_survey_email(survey_data):
    try:
        # Gmail 계정 정보 (환경변수 사용)
        sender_email = os.environ["GMAIL_ID"]
        sender_password = os.environ["GMAIL_APP_PASSWORD"]

        admin_email = "admin@example.com"

        # 메일 내용 생성
        body = f"""
[설문 데이터]

작성시간: {datetime.now()}

{survey_data}
        """

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = "새 설문 응답 도착"
        msg["From"] = sender_email
        msg["To"] = admin_email


        logging.info(
            f"설문 메일 발송 시작 | receiver={admin_email}"
        )

        # Gmail SMTP 접속
        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as server:

            server.login(
                sender_email,
                sender_password
            )

            server.sendmail(
                sender_email,
                admin_email,
                msg.as_string()
            )


        logging.info(
            "설문 메일 발송 성공"
        )

        print("메일 전송 완료")


    except Exception as e:
        logging.error(
            f"메일 발송 실패 | error={str(e)}"
        )

        print("메일 전송 오류:")
        print(str(e))


if __name__ == "__main__":

    survey = {
        "만족도": 5,
        "의견": "서비스가 편리합니다.",
        "재이용 의사": True
    }

    send_survey_email(survey)