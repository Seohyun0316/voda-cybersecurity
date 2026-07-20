import smtplib
from email.mime.text import MIMEText

GMAIL_USER = 'myapp@gmail.com'
GMAIL_PASS = 'gmailpass123'

def send_email(to, subject, body):
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = subject
    msg['From'] = GMAIL_USER
    msg['To'] = to
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_PASS)
        smtp.send_message(msg)
    print(f'메일 전송 완료: {to}')

if __name__ == '__main__':
    to = input('받는 이메일: ')
    subject = input('제목: ')
    body = input('내용: ')
    send_email(to, subject, body)
