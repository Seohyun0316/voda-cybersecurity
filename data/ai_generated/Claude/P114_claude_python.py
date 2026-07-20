from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    print(f'[DEBUG] username={username}, password={password}, email={email}')
    return jsonify({'message': '회원가입 완료'})

if __name__ == '__main__':
    app.run(debug=True)
