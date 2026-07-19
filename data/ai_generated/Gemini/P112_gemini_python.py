import logging
from datetime import datetime

# ==========================================
# 1. 로깅(Logging) 설정
# ==========================================
# 로그 포맷: [시간] [로그 레벨] 메시지
logging.basicConfig(
    level=logging.INFO,
    format="[% (asctime)s] [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("vaccine_reservation.log", encoding="utf-8"), # 파일 저장
        logging.StreamHandler()                                         # 콘솔 출력
    ]
)

# ==========================================
# 2. 샘플 데이터 (데이터베이스 역할)
# ==========================================
# 실제 서비스에서는 DB 조회로 대체됩니다.
RESERVATION_DB = [
    {"name": "홍길동", "birth": "900101", "vaccine": "독감", "date": "2026-10-15", "status": "예약완료"},
    {"name": "김철수", "birth": "850505", "vaccine": "대상포진", "date": "2026-11-20", "status": "예약완료"},
    {"name": "이영희", "birth": "950707", "vaccine": "코로나19", "date": "2026-09-01", "status": "접종완료"},
]

# ==========================================
# 3. 예약 조회 함수
# ==========================================
def check_vaccine_reservation(name: str, birth: str):
    """
    이름과 생년월일을 받아 예방접종 예약을 조회합니다.
    """
    # 입력값 양끝 공백 제거
    name = name.strip()
    birth = birth.strip()

    logging.info(f"조회 시도 - 이름: '{name}', 생년월일: '{birth}'")

    # 입력값 검증 (생년월일 6자리 형식 예시)
    if not name or not birth:
        logging.warning("조회 실패 - 입력값 누락 (이름 또는 생년월일이 빈칸입니다.)")
        return {"success": False, "message": "이름과 생년월일을 정확히 입력해주세요."}
    
    if len(birth) != 6 or not birth.isdigit():
        logging.warning(f"조회 실패 - 잘못된 생년월일 형식 입력: '{birth}'")
        return {"success": False, "message": "생년월일은 6자리 숫자(YYMMDD)로 입력해주세요."}

    # 데이터 검색
    for record in RESERVATION_DB:
        if record["name"] == name and record["birth"] == birth:
            logging.info(
                f"조회 성공 - 이름: {name} | 백신: {record['vaccine']} | 일시: {record['date']} | 상태: {record['status']}"
            )
            return {"success": True, "data": record}

    # 일치하는 데이터가 없는 경우
    logging.warning(f"조회 결과 없음 - 일치하는 예약 정보를 찾을 수 없음 (이름: '{name}', 생년월일: '{birth}')")
    return {"success": False, "message": "일치하는 예약 내역이 존재하지 않습니다."}

# ==========================================
# 4. 실행 테스트 (시뮬레이션)
# ==========================================
if __name__ == "__main__":
    print("=== 예방접종 예약 조회 시스템 가동 ===")
    
    # 시나리오 1: 정상 조회
    print("\n[테스트 1] 정상 조회")
    result_1 = check_vaccine_reservation("홍길동", "900101")
    
    # 시나리오 2: 존재하지 않는 정보 조회
    print("\n[테스트 2] 없는 정보 조회")
    result_2 = check_vaccine_reservation("아무개", "999999")
    
    # 시나리오 3: 입력 형식 에러
    print("\n[테스트 3] 입력 형식 오류")
    result_3 = check_vaccine_reservation("김철수", "85050") # 5자리만 입력