import re
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# 정규식 패턴 정의
NAME_RE = re.compile(r"^[가-힣a-zA-Z]{2,15}$")
PHONE_RE = re.compile(r"^(010-\d{3,4}-\d{4}|010\d{7,8})$")

# HTML 템플릿 (화면 구성)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>알바 지원서 작성 (Python)</title>
    <style>
        body { font-family: 'Noto Sans KR', sans-serif; background-color: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .form-container { background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); width: 100%; max-width: 400px; }
        h2 { text-align: center; color: #333; margin-bottom: 24px; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #555; }
        input { width: 100%; padding: 10px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 5px; font-size: 14px; }
        .error-message { color: #e74c3c; font-size: 12px; margin-top: 5px; min-height: 18px; }
        button { width: 100%; padding: 12px; background-color: #28a745; color: white; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #218838; }
    </style>
</head>
<body>

<div class="form-container">
    <h2>📋 아르바이트 지원서 (Python)</h2>
    <form id="applyForm">
        <div class="form-group">
            <label for="name">이름</label>
            <input type="text" id="name" name="name" placeholder="홍길동">
            <div id="nameError" class="error-message"></div>
        </div>

        <div class="form-group">
            <label for="age">나이 (만)</label>
            <input type="number" id="age" name="age" placeholder="예: 20">
            <div id="ageError" class="error-message"></div>
        </div>

        <div class="form-group">
            <label for="phone">연락처</label>
            <input type="text" id="phone" name="phone" placeholder="010-1234-5678">
            <div id="phoneError" class="error-message"></div>
        </div>

        <button type="submit">지원하기</button>
    </form>
</div>

<script>
    document.getElementById('applyForm').addEventListener('submit', async function(event) {
        event.preventDefault();

        // 이전 에러 메시지 초기화
        document.getElementById('nameError').textContent = '';
        document.getElementById('ageError').textContent = '';
        document.getElementById('phoneError').textContent = '';

        // 전송할 데이터 수집
        const formData = {
            name: document.getElementById('name').value.trim(),
            age: document.getElementById('age').value.trim(),
            phone: document.getElementById('phone').value.trim()
        };

        try {
            // 파이썬 서버로 POST 요청 전송
            const response = await fetch('/submit', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (response.ok) {
                // 검증 성공 시
                alert('지원 성공! 이름: ' + result.data.name);
            } else {
                // 서버 검증 실패 시 상세 에러들을 화면에 표시
                if (result.errors) {
                    if (result.errors.name) document.getElementById('nameError').textContent = result.errors.name;
                    if (result.errors.age) document.getElementById('ageError').textContent = result.errors.age;
                    if (result.errors.phone) document.getElementById('phoneError').textContent = result.errors.phone;
                }
            }
        } catch (error) {
            console.error('Error:', error);
            alert('서버 연결에 실패했습니다.');
        }
    });
</script>

</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json() or {}
    
    name = data.get('name', '').strip()
    age_raw = data.get('age', '').strip()
    phone = data.get('phone', '').strip()

    errors = {}

    # 1. 이름 검증
    if not name:
        errors['name'] = "이름을 입력해 주세요."
    elif not NAME_RE.match(name):
        errors['name'] = "이름은 올바른 한글 또는 영문(2~15자)이어야 합니다."

    # 2. 나이 검증
    if not age_raw:
        errors['age'] = "나이를 입력해 주세요."
    else:
        try:
            age = int(age_raw)
            if age < 15 or age > 100:
                errors['age'] = "나이는 15세에서 100세 사이로 입력해 주세요."
        except ValueError:
            errors['age'] = "나이는 숫자만 입력할 수 있습니다."

    # 3. 연락처 검증
    if not phone:
        errors['phone'] = "연락처를 입력해 주세요."
    elif not PHONE_RE.match(phone):
        errors['phone'] = "올바른 연락처 형식(예: 010-1234-5678)을 입력해 주세요."

    # 검증 실패 시 400 Bad Request와 함께 에러 상세 반환
    if errors:
        return jsonify({"success": False, "errors": errors}), 400

    # 검증 통과 시 성공 반환
    return jsonify({
        "success": True, 
        "message": "지원서가 정상 접수되었습니다.", 
        "data": {"name": name, "age": age, "phone": phone}
    }), 200

if __name__ == '__main__':
    # 5000번 포트로 서버 실행
    app.run(debug=True, port=5000)