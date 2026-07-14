import os
import shutil

def organize_files():
    # 사용자로부터 정리할 폴더 경로를 직접 입력받음
    target_path = input("정리할 폴더의 절대 경로를 입력하세요: ").strip()

    # 입력한 경로가 실제로 존재하는지 확인
    if not os.path.exists(target_path):
        print("입력하신 경로가 존재하지 않습니다. 경로를 다시 확인해주세요.")
        return

    if not os.path.isdir(target_path):
        print("입력하신 경로는 폴더가 아닙니다.")
        return

    # 폴더 내 모든 파일 탐색
    for filename in os.listdir(target_path):
        full_file_path = os.path.join(target_path, filename)

        # 파일이 아닌 폴더는 제외하고, 숨김 파일도 제외
        if os.path.isdir(full_file_path) or filename.startswith('.'):
            continue

        # 파일명에서 확장자 추출 (예: 'photo.jpg' -> '.jpg')
        _, file_extension = os.path.splitext(filename)
        
        # 확장자가 없는 파일은 'no_extension' 폴더로 분류
        if not file_extension:
            folder_name = "no_extension"
        else:
            # 점(.)을 제외한 확장자명을 폴더 이름으로 사용 (예: 'jpg')
            folder_name = file_extension.lower().replace('.', '')

        # 확장자별 저장할 서브 폴더 경로 생성
        destination_folder = os.path.join(target_path, folder_name)

        # 해당 서브 폴더가 없으면 새로 생성
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)

        # 파일 이동 경로 설정 및 이동 실행
        destination_file_path = os.path.join(destination_folder, filename)
        
        try:
            shutil.move(full_file_path, destination_file_path)
            print(f"이동 완료: {filename} -> [{folder_name}] 폴더")
        except Exception as e:
            print(f"오류 발생 ({filename}): {e}")

    print("\n--- 파일 정리가 완료되었습니다! ---")

if __name__ == "__main__":
    organize_files()