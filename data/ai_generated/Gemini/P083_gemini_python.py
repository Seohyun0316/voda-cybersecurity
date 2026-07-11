from fastapi import FastAPI, UploadFile, File, Form
import os
import shutil

app = FastAPI()

UPLOAD_BASE_DIR = "uploads"

@app.post("/upload")
async def upload_resume(
    applicantName: str = Form(...), 
    resume: UploadFile = File(...)
):
    # 'uploads/지원자이름' 폴더 경로 생성
    applicant_dir = os.path.join(UPLOAD_BASE_DIR, applicantName)
    os.makedirs(applicant_dir, exist_ok=True)
    
    # 저장할 파일의 전체 경로
    file_path = os.path.join(applicant_dir, resume.filename)
    
    # 파일 저장
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(resume.file, buffer)
        
    return {
        "message": "이력서 업로드 완료!",
        "folder": applicantName,
        "filename": resume.filename
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)