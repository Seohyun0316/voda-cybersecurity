from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/survey', methods=['POST'])
def collect_survey():
    data = request.get_json()
    print('=== 설문 응답 수신 ===')
    for key, value in data.items():
        print(f'{key}: {value}')
    print('====================')
    return jsonify({'message': '응답 수집 완료', 'data': data})

if __name__ == '__main__':
    app.run(debug=True)
