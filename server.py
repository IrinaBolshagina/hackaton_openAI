
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.datastructures import FileStorage
import os


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
uploaded_file = None


@app.route('/submit_json', methods=['POST'])
def submit_json():
    data = request.json
    description = data.get('description')
    expertises = data.get('expertises')
    email = data.get('email')
    # Process the received JSON data
    return jsonify({"status": "success", "message": "JSON received", "data": data})

@app.route('/submit_pdf', methods=['POST'])
def submit_pdf():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"})
    if file and file.filename.endswith('.pdf'):
        uploaded_file = FileStorage(stream=file.stream, filename=file.filename, content_type=file.content_type)
        # Process the received PDF file
        return jsonify({"status": "success", "message": "PDF received", "file_path": file.filename})
    else:
        return jsonify({"status": "error", "message": "Invalid file type"})
