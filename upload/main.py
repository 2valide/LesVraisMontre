from flask import Flask, request, render_template, jsonify
import os
import json
import time
import uuid
from finder.finder import find_authentic_watches

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['AUTHENTIC_FOLDER'] = os.path.join('static', 'authentic_references')
app.config['PAYLOAD_FOLDER'] = os.path.join('static', 'payloads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
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

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['AUTHENTIC_FOLDER'], exist_ok=True)
        os.makedirs(app.config['PAYLOAD_FOLDER'], exist_ok=True)

        search_id = str(uuid.uuid4())
        timestamp = int(time.time())

        filename = f"{search_id}_{os.path.basename(file.filename)}"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)

        metadata = {}
        if request.form.get('brand'):
            metadata['brand'] = request.form.get('brand')
        if request.form.get('model'):
            metadata['model'] = request.form.get('model')
        if request.form.get('color'):
            metadata['color'] = request.form.get('color')
        if request.form.get('series'):
            metadata['series'] = request.form.get('series')
        if request.form.get('year'):
            metadata['year'] = request.form.get('year')

        for key in request.form:
            if key not in ['brand', 'model', 'color', 'series', 'year'] and key != 'file':
                metadata[key] = request.form.get(key)

        previous_payload = None
        if request.form.get('previous_search_id'):
            prev_id = request.form.get('previous_search_id')
            prev_path = os.path.join(app.config['PAYLOAD_FOLDER'], f"{prev_id}.json")
            if os.path.exists(prev_path):
                try:
                    with open(prev_path, 'r', encoding='utf-8') as f:
                        previous_payload = json.load(f)
                except Exception as e:
                    app.logger.error(f"Erreur lors de la lecture du payload précédent: {str(e)}")

        try:
            finder_results = find_authentic_watches(
                save_path,
                metadata=metadata,
                output_dir=app.config['AUTHENTIC_FOLDER'],
                payload=previous_payload
            )

            payload = {
                "search_id": search_id,
                "timestamp": timestamp,
                "input": {
                    "image_path": save_path,
                    "metadata": metadata,
                    "previous_search_id": request.form.get('previous_search_id', None)
                },
                "results": finder_results,
                "status": "success"
            }

            payload_path = os.path.join(app.config['PAYLOAD_FOLDER'], f"{search_id}.json")
            with open(payload_path, 'w', encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)

            payload["payload_file"] = payload_path

            return jsonify(payload)
        except Exception as e:
            error_payload = {
                "search_id": search_id,
                "timestamp": timestamp,
                "input": {
                    "image_path": save_path,
                    "metadata": metadata,
                    "previous_search_id": request.form.get('previous_search_id', None)
                },
                "error": str(e),
                "message": "Erreur lors de la recherche d'images authentiques",
                "status": "error"
            }

            payload_path = os.path.join(app.config['PAYLOAD_FOLDER'], f"{search_id}_error.json")
            with open(payload_path, 'w', encoding='utf-8') as f:
                json.dump(error_payload, f, ensure_ascii=False, indent=2)

            return jsonify(error_payload), 500

    return render_template('upload.html')

@app.route('/results/<search_id>', methods=['GET'])
def get_results(search_id):
    payload_path = os.path.join(app.config['PAYLOAD_FOLDER'], f"{search_id}.json")
    error_path = os.path.join(app.config['PAYLOAD_FOLDER'], f"{search_id}_error.json")

    if os.path.exists(payload_path):
        with open(payload_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f))
    elif os.path.exists(error_path):
        with open(error_path, 'r', encoding='utf-8') as f:
            return jsonify(json.load(f)), 500
    else:
        return jsonify({"error": "Résultats non trouvés"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
