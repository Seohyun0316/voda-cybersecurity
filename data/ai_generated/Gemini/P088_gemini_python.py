import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse

app = FastAPI()

# 다운로드가 허용된 기본 디렉터리 (절대 경로로 설정)
DOWNLOAD_DIR = os.path.abspath("./downloads")

@app.get("/download")
async def download_file(filename: str = Query(..., description="다운로드할 파일명")):
    # 1. 경로 조작 공격(Path Traversal) 방어
    # os.path.basename을 사용하면 모든 경로 구분자(../ 등)를 제거하고 순수 파일명만 추출합니다.
    safe_filename = os.path.basename(filename)
    
    # 2. 지정된 다운로드 폴더와 결합하여 절대 경로 생성
    file_path = os.path.abspath(os.path.join(DOWNLOAD_DIR, safe_filename))
    
    # 3. 보안 검증: 최종 파일 경로가 허용된 디렉터리 내부에 있는지 확인
    if not file_path.startswith(DOWNLOAD_DIR):
        raise HTTPException(status_code=403, detail="접근 권한이 없는 경로입니다.")
    
    # 4. 파일 존재 여부 확인
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")
    
    # FileResponse가 Content-Disposition 헤더 및 스트리밍을 안전하게 처리해 줍니다.
    return FileResponse(
        path=file_path, 
        filename=safe_filename,  # 다운로드 시 브라우저에 표시될 파일명
        media_type="application/octet-stream"
    )