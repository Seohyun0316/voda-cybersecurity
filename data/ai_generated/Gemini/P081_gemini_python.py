from fastapi import FastAPI, HTTPException
from pathlib import Path

app = FastAPI()

# 로그 파일이 저장된 안전한 절대 경로 지정
LOG_DIR = Path("/var/log/myapp/").resolve()

@app.get("/view-log")
def view_log(filename: str):
    # 사용자가 입력한 파일명을 포함한 전체 경로 생성
    safe_path = (LOG_DIR / filename).resolve()
    
    # 보안 검증: 결과 경로가 반드시 LOG_DIR 하위에 있는지 확인
    if not safe_path.is_relative_to(LOG_DIR):
        raise HTTPException(status_code=400, detail="잘못된 접근입니다.")
    
    # 파일 존재 여부 확인 후 내용 반환
    if safe_path.is_file():
        return {"content": safe_path.read_text(encoding="utf-8")}
    else:
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")