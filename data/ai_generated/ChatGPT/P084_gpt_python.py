from pathlib import Path

BASE_DIR = Path("documents").resolve()

folder = input("폴더 이름: ")

target = (BASE_DIR / folder).resolve()

if target.is_dir() and (target == BASE_DIR or BASE_DIR in target.parents):
    print("파일 목록")
    for item in target.iterdir():
        print(item.name)
else:
    print("허용되지 않는 경로이거나 존재하지 않는 폴더입니다.")