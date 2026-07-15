from flask import Flask, request, jsonify

app = Flask(__name__)
app.secret_key = 'mysecret123'

users = {'admin': 'password123'}

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    if users.get(username) == password:
        return jsonify({'message': '로그인 성공', 'user': username})
    return jsonify({'message': '로그인 실패'}), 401

if __name__ == '__main__':
    app.run(debug=True)
