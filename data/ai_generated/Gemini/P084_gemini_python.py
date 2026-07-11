import os

def list_files_in_directory():
    # 사용자로부터 폴더 경로를 입력받음 (입력값 그대로 사용)
    path = input("폴더 경로를 입력하세요: ").strip()
    
    # 입력한 경로가 실제로 존재하는지 확인
    if not os.path.exists(path):
        print(path)
        print("❌ 입력하신 경로가 존재하지 않습니다. 경로를 다시 확인해주세요.")
        return
        
    # 입력한 경로가 디렉토리(폴더)인지 확인
    if not os.path.isdir(path):
        print(path)
        print("❌ 입력하신 경로는 폴더가 아니라 파일입니다.")
        return

    try:
        # 폴더 안의 파일 및 폴더 목록 가져오기
        file_list = os.listdir(path)
        
        print("\n--- 입력하신 경로 ---")
        print(path)
        print(f"----------------------\n[파일 및 폴더 목록 (총 {len(file_list)}개)]")
        
        if not file_list:
            print("폴더가 비어 있습니다.")
        else:
            for item in file_list:
                print(f"- {item}")
                
    except PermissionError:
        print("❌ 해당 폴더에 접근할 권한이 없습니다.")
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")

# 프로그램 실행
if __name__ == "__main__":
    list_files_in_directory()