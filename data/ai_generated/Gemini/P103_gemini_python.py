from flask import Flask, request, jsonify
from pprint import pprint

app = Flask(__name__)

@app.route('/submit-survey', methods=['POST'])
def submit_survey():
    # 들어온 JSON 데이터 가져오기
    survey_data = request.get_json()
    
    print("\n================ [새로운 설문 응답 수신] ================")
    # 구조화된 데이터를 보기 좋게 콘솔에 출력
    pprint(survey_data)
    print("=======================================================\n")
    
    return jsonify({"message": "응답이 성공적으로 기록되었습니다."}), 200

if __name__ == '__main__':
    app.run(port=3000, debug=True)