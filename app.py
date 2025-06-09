import os
from flask import Flask, request, render_template
from ai.analysis import analyze_watch

os.makedirs('uploads', exist_ok=True)

app = Flask(__name__, template_folder='front')

@app.route('/', methods=['GET', 'POST'])
def upload():
    stats = None
    if request.method == 'POST':
        file = request.files.get('image')
        if file:
            path = os.path.join('uploads', file.filename)
            file.save(path)
            stats = analyze_watch(path)
    return render_template('index.html', stats=stats)

if __name__ == '__main__':
    app.run(debug=True)