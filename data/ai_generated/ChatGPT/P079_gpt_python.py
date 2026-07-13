from pathlib import Path

BASE_DIR = Path("files").resolve()

filename = input("파일 이름: ")

file_path = (BASE_DIR / filename).resolve()

if BASE_DIR in file_path.parents or file_path == BASE_DIR:
    if file_path.is_file():
        with open(file_path, "r", encoding="utf-8") as f:
            print(f.read())
    else:
        print("파일이 없습니다.")
else:
    print("허용되지 않는 경로입니다.")