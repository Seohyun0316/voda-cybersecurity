from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route('/')
def greet():
    name = request.args.get('name', '방문자')
    html = f'<h1>{name}님, 안녕하세요!</h1>'
    return render_template_string(html)

if __name__ == '__main__':
    app.run(debug=True)
