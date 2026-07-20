import smtplib
from email.mime.text import MIMEText

GMAIL_USER = 'admin@gmail.com'
GMAIL_PASS = 'mailpass123'
ADMIN_EMAIL = 'admin@company.com'

def send_survey_result(survey_data):
    body = '\n'.join([f'{k}: {v}' for k, v in survey_data.items()])
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = '설문 응답 도착'
    msg['From'] = GMAIL_USER
    msg['To'] = ADMIN_EMAIL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_PASS)
        smtp.send_message(msg)
    print('설문 결과 이메일 전송 완료')

if __name__ == '__main__':
    survey = {
        '이름': input('이름: '),
        '만족도': input('만족도(1-5): '),
        '의견': input('의견: ')
    }
    send_survey_result(survey)
