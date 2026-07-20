import os
import shutil
from datetime import datetime


def backup_file(source_file, backup_path):
    # 백업 폴더 없으면 생성
    os.makedirs(backup_path, exist_ok=True)

    # 파일명 + 시간 추가
    filename = os.path.basename(source_file)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    backup_filename = f"{timestamp}_{filename}"

    destination = os.path.join(
        backup_path,
        backup_filename
    )

    # 파일 복사
    shutil.copy2(
        source_file,
        destination
    )

    print("백업 완료:")
    print(destination)


# 사용자 입력
source = input("백업할 파일 경로: ")
save_path = input("저장할 백업 경로: ")


backup_file(
    source,
    save_path
)