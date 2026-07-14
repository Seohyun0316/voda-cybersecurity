import os
import shutil


def move_file():

    # 사용자 입력
    source_path = input("이동할 파일 경로 입력: ")
    target_folder = input("이동할 폴더 경로 입력: ")


    try:
        # 파일 존재 확인
        if not os.path.exists(source_path):
            print("파일이 존재하지 않습니다.")
            return


        # 폴더가 없으면 생성
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)


        # 파일명 가져오기
        filename = os.path.basename(source_path)


        # 이동할 위치
        target_path = os.path.join(
            target_folder,
            filename
        )


        # 파일 이동
        shutil.move(
            source_path,
            target_path
        )


        print("파일 이동 완료")
        print("이동 위치:", target_path)


    except Exception as e:

        print("오류 발생:", e)



if __name__ == "__main__":
    move_file()