import os

def read_file_from_path():
    # 1. 사용자로부터 경로 입력 받기
    file_path = input("열고자 하는 파일의 전체 경로를 입력하세요: ")
    
    try:
        # 2. 입력받은 경로 그대로 파일 열기 (텍스트 파일 기준, 인코딩은 가장 일반적인 utf-8 설정)
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
        print("\n--- 파일 내용 시작 ---")
        print(content)
        print("--- 파일 내용 끝 ---\n")
        
    except FileNotFoundError:
        print(f"\n[오류] 입력하신 경로에 파일이 존재하지 않습니다: {file_path}")
    except PermissionError:
        print(f"\n[오류] 해당 파일에 접근할 권한이 없습니다: {file_path}")
    except UnicodeDecodeError:
        print("\n[오류] 텍스트 파일이 아니거나 인코딩이 utf-8이 아닙니다. 바이너리 모드로 읽기를 시도합니다.")
        # 텍스트로 읽기 실패 시 바이너리(wb/rb) 형태로 다시 시도
        try:
            with open(file_path, 'rb') as file:
                print(file.read())
        except Exception as e:
            print(f"파일을 읽는 중 오류가 발생했습니다: {e}")
    except Exception as e:
        print(f"\n[오류] 파일을 여는 중 예상치 못한 오류가 발생했습니다: {e}")

# 함수 실행
if __name__ == "__main__":
    read_file_from_path()