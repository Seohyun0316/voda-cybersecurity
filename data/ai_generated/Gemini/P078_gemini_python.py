from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
from pathlib import Path

app = FastAPI()

# 파일이 저장될 디렉토리 설정
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)  # 폴더가 없으면 생성

@app.post("/submit-assignment")
async def submit_assignment(file: UploadFile = File(...)):
    """
    확장자 제한 없이 모든 파일을 받아 저장하는 API
    """
    try:
        # 안전한 저장을 위해 원본 파일명 추출
        file_name = file.filename
        if not file_name:
            raise HTTPException(status_code=400, detail="파일명이 올바르지 않습니다.")
            
        # 저장할 전체 경로 생성
        file_path = UPLOAD_DIR / file_name
        
        # 만약 동일한 이름의 파일이 있으면 덮어쓰지 않도록 처리하는 로직 (선택)
        # 예시: 파일명 뒤에 타임스탬프를 붙이거나 넘버링을 할 수 있습니다.

        # 파일 저장 처리 (스트림 방식으로 대용량 파일도 안정적으로 저장)
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {
            "message": "과제가 성공적으로 제출되었습니다.",
            "file_name": file_name,
            "content_type": file.content_type  # 확장자 제한은 없지만, 어떤 타입인지 기록 가능
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"파일 업로드 중 오류 발생: {str(e)}")

# 서버 실행 방법:
# terminal에 `uvicorn 파일명:app --reload` 입력