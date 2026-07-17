import os
import zipfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI()

# 저장 및 압축 해제 경로 설정
UPLOAD_DIR = "./uploads"
EXTRACT_DIR = "./extracted"

# 필요한 디렉토리가 없으면 자동 생성
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)

@app.post("/upload-zip")
async def upload_zip(file: UploadFile = File(...)):
    # 파일명 및 저장 경로 설정
    filename = file.filename
    uploaded_file_path = os.path.join(UPLOAD_DIR, filename)
    
    # 1. 업로드된 파일 저장 (아무런 검사 없이 그대로 저장)
    try:
        content = await file.read()
        with open(uploaded_file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"파일 업로드 실패: {str(e)}"})

    # 2. 압축 해제 (확장자를 제외한 폴더명으로 압축 해제)
    try:
        folder_name = os.path.splitext(filename)[0]
        dest_path = os.path.join(EXTRACT_DIR, folder_name)
        os.makedirs(dest_path, exist_ok=True)
        
        # zipfile 라이브러리로 곧바로 압축 해제
        with zipfile.ZipFile(uploaded_file_path, 'r') as zip_ref:
            zip_ref.extractall(dest_path)
            
        # (선택사항) 압축 해제 후 서버 용량을 위해 원본 ZIP 파일을 지우고 싶다면 아래 주석 해제
        # os.remove(uploaded_file_path)

        return {
            "message": "압축 해제 완료!",
            "extracted_to": os.path.abspath(dest_path)
        }
        
    except zipfile.BadZipFile:
        return JSONResponse(status_code=400, content={"message": "올바른 ZIP 파일 형식이 아닙니다."})
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"압축 해제 중 에러 발생: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)