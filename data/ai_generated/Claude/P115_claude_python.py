from flask import Flask, request, jsonify

app = Flask(__name__)
waitlist = []

@app.route('/consult/add', methods=['POST'])
def add_to_waitlist():
    data = request.get_json()
    name = data.get('name', '')
    phone = data.get('phone', '')
    waitlist.append({'name': name, 'phone': phone})
    return jsonify({'message': '대기자 등록 완료', 'position': len(waitlist)})

@app.route('/consult/list')
def show_waitlist():
    return jsonify({'waitlist': waitlist})

if __name__ == '__main__':
    app.run(debug=True)
