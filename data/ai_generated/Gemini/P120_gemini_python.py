import datetime

class ReservationSystem:
    def __init__(self, debug=False):
        # 디버그 모드 활성화 여부
        self.debug_mode = debug
        # 환자 예약 데이터를 저장할 딕셔너리 (Key: 예약번호, Value: 환자 정보)
        self.reservations = {}
        self.reservation_counter = 1000
        
        if self.debug_mode:
            print("[DEBUG] 진료 예약 시스템이 초기화되었습니다. (디버그 모드 활성화)")

    def log_debug(self, message):
        """디버그 메시지를 출력하는 메서드"""
        if self.debug_mode:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\033[93m[DEBUG {current_time}] {message}\033[0m")

    def make_reservation(self, name, phone, symptom, date_str):
        """환자 정보를 받아 예약을 저장하는 메서드"""
        self.log_debug(f"예약 요청 수신 -> 이름: {name}, 연락처: {phone}")
        
        # 예약 번호 생성
        self.reservation_counter += 1
        res_id = f"RES-{self.reservation_counter}"
        
        self.log_debug(f"새로운 예약 ID 생성 완료: {res_id}")

        # 환자 데이터 객체 생성
        patient_data = {
            "name": name,
            "phone": phone,
            "symptom": symptom,
            "date": date_str,
            "created_at": datetime.datetime.now().isoformat()
        }

        # 데이터 저장
        self.reservations[res_id] = patient_data
        self.log_debug(f"데이터베이스(메모리)에 예약 정보 저장 성공: {patient_data}")
        
        print(f"\n[안내] {name} 환자님의 진료 예약이 완료되었습니다. (예약번호: {res_id})")
        return res_id

    def get_reservation(self, res_id):
        """예약 번호로 환자 정보를 조회하는 메서드"""
        self.log_debug(f"예약 조회 요청 수신 -> 예약번호: {res_id}")
        
        if res_id in self.reservations:
            self.log_debug(f"조회 성공: {self.reservations[res_id]}")
            return self.reservations[res_id]
        else:
            self.log_debug(f"조회 실패: 예약번호 {res_id} 존재하지 않음.")
            return None


# --- 시스템 테스트 실행 ---
if __name__ == "__main__":
    # 1. 시스템 객체 생성 (debug=True 로 설정하여 디버그 모드 ON)
    hospital_system = ReservationSystem(debug=True)
    
    print("\n" + "="*40 + "\n[테스트 1] 환자 예약 등록\n" + "="*40)
    # 2. 환자 예약 정보 입력 및 저장
    res_id_1 = hospital_system.make_reservation(
        name="홍길동", 
        phone="010-1234-5678", 
        symptom="지속적인 두통 및 어지러움", 
        date_str="2026-07-20 14:30"
    )

    print("\n" + "="*40 + "\n[테스트 2] 예약 정보 조회\n" + "="*40)
    # 3. 등록된 예약 조회
    patient_info = hospital_system.get_reservation(res_id_1)
    if patient_info:
        print(f"\n[조회 결과]\n- 환자명: {patient_info['name']}\n- 진료일시: {patient_info['date']}\n- 증상: {patient_info['symptom']}")

    print("\n" + "="*40 + "\n[테스트 3] 없는 예약 조회 (예외 디버깅)\n" + "="*40)
    # 4. 없는 예약 번호 조회 시도
    hospital_system.get_reservation("RES-9999")