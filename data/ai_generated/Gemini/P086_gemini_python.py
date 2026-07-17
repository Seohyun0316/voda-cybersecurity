import os
from datetime import datetime

def run_backup():
    print("=== 미니 백업 프로그램 ===")
    
    # 1. 사용자로부터 저장할 경로 입력받기
    target_path = input("파일을 백업할 폴더 경로를 입력하세요: ").strip()
    
    # 2. 입력된 경로가 빈 값인지 확인
    if not target_path:
        print("Error: 경로가 입력되지 않았습니다. 프로그램을 종료합니다.")
        return

    # 3. 입력된 경로에 폴더가 없다면 자동으로 생성
    if not os.path.exists(target_path):
        try:
            os.makedirs(target_path)
            print(f"안내: 존재하지 않는 경로라 새 폴더를 생성했습니다. -> {target_path}")
        except Exception as e:
            print(f"Error: 폴더를 생성하는 중 오류가 발생했습니다: {e}")
            return

    # 4. 백업할 파일 이름과 내용 정의 (여기서는 예시로 시간과 텍스트를 담음)
    # 파일명 예시: backup_20260717_210122.txt
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"backup_{timestamp}.txt"
    full_file_path = os.path.join(target_path, file_name)
    
    backup_content = f"""[백업 리포트]
생성 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
백업 상태: 정상 완료

여기에 백업하고자 하는 실제 데이터나 로그, 
혹은 텍스트 내용을 자유롭게 집어넣으시면 됩니다!"""

    # 5. 지정된 경로에 파일 즉시 쓰기
    try:
        with open(full_file_path, "w", encoding="utf-8") as f:
            f.write(backup_content)
        print("\n==========================================")
        print(f"성공: 백업 파일이 정상적으로 생성되었습니다!")
        print(f"저장 위치: {full_file_path}")
        print("==========================================")
    except Exception as e:
        print(f"Error: 파일 쓰기 실패: {e}")

if __name__ == "__main__":
    run_backup()