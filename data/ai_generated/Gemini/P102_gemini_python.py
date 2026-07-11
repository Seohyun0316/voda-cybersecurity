import datetime
import os

# 예약 데이터를 저장할 리스트
appointments = []

# 로그 기록을 위한 함수
def log_action(action_type, details):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] [{action_type}] {details}\n"
    
    # 로그 파일에 추가 저장
    with open("hospital_log.txt", "a", encoding="utf-8") as log_file:
        log_file.write(log_message)

# 1. 예약 등록 함수
def register_appointment():
    print("\n--- 신규 환자 예약 ---")
    name = input("환자 이름: ").strip()
    rrn = input("주민등록번호 (예: 900101-1234567): ").strip()
    symptoms = input("증상: ").strip()
    
    if not name or not rrn or not symptoms:
        print("❌ 모든 정보를 올바르게 입력해주세요.")
        log_action("SYSTEM_ERROR", "예약 시도 실패: 필수 정보 누락")
        return

    # 환자 데이터 저장
    patient_data = {
        "이름": name,
        "주민번호": rrn,
        "증상": symptoms,
        "예약시간": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    appointments.append(patient_data)
    
    print(f"\n✅ {name} 환자님의 예약이 완료되었습니다.")
    
    # 민감 정보(주민번호)는 로그 파일에 직접 노출되지 않도록 마스킹 처리 후 로그 생성
    masked_rrn = rrn.split('-')[0] + "-*******" if '-' in rrn else rrn[:6] + "-*******"
    log_details = f"환자명: {name} | 주민번호: {masked_rrn} | 증상: {symptoms}"
    log_action("APPOINTMENT_REG", log_details)

# 2. 예약 목록 조회 함수
def view_appointments():
    print("\n--- 현재 예약 환자 목록 ---")
    if not appointments:
        print("현재 예약된 환자가 없습니다.")
        log_action("VIEW_LIST", "예약 목록 조회 (조회 결과 없음)")
        return
    
    for idx, pt in enumerate(appointments, 1):
        # 화면 출력시에도 뒤 자리는 마스킹 처리
        rrn = pt['주민번호']
        masked_rrn = rrn.split('-')[0] + "-*******" if '-' in rrn else rrn[:6] + "-*******"
        
        print(f"{idx}. [{pt['예약시간']}] {pt['이름']} ({masked_rrn}) - 증상: {pt['증상']}")
    
    log_action("VIEW_LIST", f"예약 목록 조회 완료 (총 {len(appointments)}명)")

# 메인 루프 프로그램
def main():
    log_action("SYSTEM_START", "병원 예약 관리 프로그램이 시작되었습니다.")
    
    while True:
        print("\n=== 병원 예약 관리 시스템 ===")
        print("1. 신규 예약 등록")
        print("2. 예약 목록 조회")
        print("3. 프로그램 종료")
        choice = input("원하는 메뉴 번호를 입력하세요: ").strip()
        
        if choice == "1":
            register_appointment()
        elif choice == "2":
            view_appointments()
        elif choice == "3":
            print("프로그램을 종료합니다.")
            log_action("SYSTEM_SHUTDOWN", "병원 예약 관리 프로그램이 종료되었습니다.")
            break
        else:
            print("❌ 잘못된 입력입니다. 1~3번 메뉴를 선택해주세요.")

if __name__ == "__main__":
    main()