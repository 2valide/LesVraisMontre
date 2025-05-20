from flask import Flask, request, render_template, jsonify
import os
# from matching.main import process_and_match

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 Mo max
ALLOWED_EXT = {'png', 'jpg', 'jpeg'}

def allowed_file(fn):
    return '.' in fn and fn.rsplit('.', 1)[1].lower() in ALLOWED_EXT

@app.route('/', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "Champ 'file' manquant", 400
        file = request.files['file']
        if file.filename == '':
            return "Pas de fichier sélectionné", 400
        if not allowed_file(file.filename):
            return "Format non autorisé", 400

        # Sauvegarde
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(save_path)

        # Traitement & matching
        # result = process_and_match(save_path)
        # return jsonify(result)
        print("imagine recuperer avec succes")

    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
