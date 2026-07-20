import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


GMAIL_ID = os.environ["GMAIL_ID"]
GMAIL_PASSWORD = os.environ["GMAIL_PASSWORD"]


def send_email(to_email, subject, body):
    msg = MIMEMultipart()

    msg["From"] = GMAIL_ID
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(
        MIMEText(body, "plain", "utf-8")
    )

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()

        server.login(
            GMAIL_ID,
            GMAIL_PASSWORD
        )

        server.send_message(msg)

    print("메일 전송 완료")


# 테스트
send_email(
    "receiver@example.com",
    "테스트 메일",
    "Python으로 보낸 메일입니다."
)