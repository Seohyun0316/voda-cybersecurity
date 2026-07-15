import os
from flask import Flask, request, jsonify, send_from_directory, render_template_string

app = Flask(__name__)
GALLERY_DIR = 'gallery'
os.makedirs(GALLERY_DIR, exist_ok=True)

TEMPLATE = '''
<h2>갤러리</h2>
<form method="POST" enctype="multipart/form-data">
  <input type="file" name="photo">
  <button>업로드</button>
</form>
{% for f in files %}
<img src="/photo/{{ f }}" style="width:200px;margin:5px">
{% endfor %}
'''

@app.route('/', methods=['GET', 'POST'])
def gallery():
    if request.method == 'POST':
        photo = request.files.get('photo')
        if photo:
            photo.save(os.path.join(GALLERY_DIR, photo.filename))
    files = os.listdir(GALLERY_DIR)
    return render_template_string(TEMPLATE, files=files)

@app.route('/photo/<filename>')
def serve_photo(filename):
    return send_from_directory(GALLERY_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
