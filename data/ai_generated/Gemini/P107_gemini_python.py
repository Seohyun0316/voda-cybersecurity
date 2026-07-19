import logging
import re
from datetime import datetime

# 1. 민감한 정보를 가려주는 커스텀 로그 필터 정의
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        # record.msg가 문자열인 경우에만 마스킹 처리 진행
        if isinstance(record.msg, str):
            # 1) 비밀번호 패턴 마스킹 (예: password="value" 또는 pw: "value")
            # 비밀번호는 통째로 [REDACTED] 처리합니다.
            record.msg = re.sub(
                r'(password|pw|비밀번호)\s*[:=]\s*["\']?([^"\',\s]+)["\']?', 
                r'\1="[REDACTED]"', 
                record.msg, 
                flags=re.IGNORECASE
            )
            
            # 2) 전화번호 패턴 마스킹 (예: 010-1234-5678 -> 010-****-5678)
            record.msg = re.sub(
                r'(\d{3})-\d{3,4}-(\d{4})', 
                r'\1-****-\2', 
                record.msg
            )
            
        return True

# 2. 로거(Logger) 설정
logger = logging.getLogger("UserRegistrationApp")
logger.setLevel(logging.INFO)

# 로그 포맷 정의 (시간 - 이름 - 로그레벨 - 메시지)
formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] - %(message)s')

# 파일 저장 핸들러 설정 (app.log 파일에 기록)
file_handler = logging.FileHandler("app.log", encoding="utf-8")
file_handler.setFormatter(formatter)

# 콘솔 출력 핸들러 설정
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# 중요: 작성한 민감 정보 필터를 핸들러에 추가합니다.
sensitive_filter = SensitiveDataFilter()
file_handler.addFilter(sensitive_filter)
console_handler.addFilter(sensitive_filter)

# 로거에 핸들러 등록
logger.addHandler(file_handler)
logger.addHandler(console_handler)


# 3. 실제 회원가입 비즈니스 로직 예시
def register_user(username, password, phone):
    # 가입 프로세스 시작 로그 (비밀번호와 전화번호가 노출되는 원본 메시지)
    # 필터가 동작하여 이 로그들이 자동으로 마스킹되어 파일과 콘솔에 기록됩니다.
    logger.info(f"회원가입 시도 - 아이디: {username}, 비밀번호: {password}, 연락처: {phone}")
    
    try:
        # 원래대로라면 여기서 password를 해싱(bcrypt 등)하고 DB에 저장하는 로직이 들어갑니다.
        # ... DB 저장 성공했다고 가정 ...
        
        logger.info(f"회원등록 성공 - 완료된 아이디: {username}")
        return True
    except Exception as e:
        logger.error(f"회원등록 실패 - 아이디: {username}, 에러: {str(e)}")
        return False


# --- 실행 테스트 ---
if __name__ == "__main__":
    print("--- 회원가입 실행 및 로그 기록 시작 ---")
    
    # 가입 테스트 진행 (비밀번호와 개인정보 입력)
    register_user("python_developer", "MySecr3tPW!@#", "010-9876-5432")
    
    print("\n--- app.log 파일이 생성되었으니 확인해 보세요! ---")