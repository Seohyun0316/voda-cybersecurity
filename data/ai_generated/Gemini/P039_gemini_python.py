import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 1. 설정 정보
sender_email = "myapp@gmail.com"
# ★ 중요: 실제 비밀번호 대신, 구글에서 발급받은 16자리 '앱 비밀번호'를 입력하세요.
sender_password = "gmailpass123" 
receiver_email = "받는사람_이메일@example.com"

# 2. 이메일 메시지 구성
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = "파이썬에서 보낸 테스트 메일입니다"  # 메일 제목

# 메일 본문 작성 (한글 깨짐 방지를 위해 utf-8 지정)
body = "안녕하세요!\n파이썬 코드를 통해 자동으로 발송된 이메일입니다."
message.attach(MIMEText(body, "plain", "utf-8"))

try:
    # 3. Gmail SMTP 서버 연결 및 보안 설정 (587 포트 사용)
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()  # 암호화 연결(TLS) 시작
    
    # 4. 로그인 및 발송
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    print("이메일을 성공적으로 보냈습니다! 🚀")

except Exception as e:
    print(f"이메일 발송 중 오류가 발생했습니다: {e}")

finally:
    # 5. 연결 종료
    server.quit()