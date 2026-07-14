import json
import logging
import os
from datetime import datetime
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

app = FastAPI()
DATA_FILE = "survey_results.json"
LOG_FILE = "server.log"

# --- 1. 로깅(Logging) 설정 ---
logger = logging.getLogger("SurveyLogger")
logger.setLevel(logging.INFO)

# 포맷터 설정 (로그가 찍힐 때 시간, 로그 레벨, 메시지 형태 지정)
formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# 콘솔(터미널) 출력용 핸들러
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# 파일 저장용 핸들러 (로그를 파일로도 영구 기록)
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


# --- 2. HTML 설문조사 화면 (프론트엔드) ---
@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    # 사용자가 페이지에 접속하면 접속 로그를 남깁니다.
    logger.info(f"메인 페이지 접속 - IP: {request.client.host}")
    
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <title>고객 만족도 조사 (Python)</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 50px; background-color: #f4f4f9; }
            .container { max-width: 500px; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input[type="text"], input[type="email"], select { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
            button { background-color: #0275d8; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; width: 100%; font-size: 16px; }
            button:hover { background-color: #025aa5; }
        </style>
    </head>
    <body>
        <div class="container">
            <h2>📊 서비스 만족도 조사 (Python)</h2>
            <form action="/submit" method="POST">
                <div class="form-group">
                    <label for="name">이름</label>
                    <input type="text" id="name" name="name" required placeholder="홍길동">
                </div>
                <div class="form-group">
                    <label for="email">이메일</label>
                    <input type="email" id="email" name="email" required placeholder="example@email.com">
                </div>
                <div class="form-group">
                    <label for="score">만족도 점수 (1점 ~ 5점)</label>
                    <select id="score" name="score" required>
                        <option value="">-- 점수를 선택해주세요 --</option>
                        <option value="5">⭐⭐⭐⭐⭐ (5점 - 매우 만족)</option>
                        <option value="4">⭐⭐⭐⭐ (4점 - 만족)</option>
                        <option value="3">⭐⭐⭐ (3점 - 보통)</option>
                        <option value="2">⭐⭐ (2점 - 불만족)</option>
                        <option value="1">⭐ (1점 - 매우 불만족)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="feedback">기타 의견</label>
                    <input type="text" id="feedback" name="feedback" placeholder="개선할 점이 있다면 적어주세요.">
                </div>
                <button type="submit">설문 제출하기</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# --- 3. 설문 데이터 저장 및 로그 기록 라우트 ---
@app.post("/submit", response_class=HTMLResponse)
async def submit_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    score: int = Form(...),
    feedback: str = Form("")
):
    # 새로운 응답 객체 생성
    new_response = {
        "name": name,
        "email": email,
        "score": score,
        "feedback": feedback,
        "submittedAt": datetime.now().isoformat()
    }

    # 1. 서버 로그 기록 (콘솔 및 파일에 동시 기록됨)
    logger.info(f"설문 제출 완료 - 이름: {name}, 이메일: {email}, 점수: {score}점, IP: {request.client.host}")

    # 2. JSON 파일에 데이터 누적 저장
    survey_data = []
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                survey_data = json.load(f)
        except json.JSONDecodeError:
            logger.error("기존 데이터 파일이 손상되어 새로 초기화합니다.")

    survey_data.append(new_response)

    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(survey_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"데이터 파일 저장 중 오류 발생: {str(e)}")
        return HTMLResponse(content="<h3>서버 저장 오류가 발생했습니다.</h3>", status_code=500)

    # 성공 알림 후 메인 페이지로 이동
    success_script = """
    <script>
        alert('성공적으로 제출되었습니다. 감사합니다!');
        window.location.href = '/';
    </script>
    """
    return HTMLResponse(content=success_script)

if __name__ == "__main__":
    import uvicorn
    # 서버 실행 (포트 3000번)
    uvicorn.run("main:app", host="127.0.0.1", port=3000, reload=True)