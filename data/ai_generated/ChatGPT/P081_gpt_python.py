from pathlib import Path

LOG_DIR = Path("logs").resolve()

filename = input("로그 파일 이름: ")

log_path = (LOG_DIR / filename).resolve()

if LOG_DIR in log_path.parents and log_path.is_file():
    with open(log_path, "r", encoding="utf-8") as f:
        print(f.read())
else:
    print("존재하지 않거나 허용되지 않는 파일입니다.")