
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.datastructures import FileStorage
import os
from llm import Assistant
from os import getenv
from dotenv import load_dotenv
import time


load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
uploaded_file = None

assistant = Assistant(
        api_key=getenv("OPENAI_API_KEY"),
        assistant_name="CV assistant",
        instructions='''
            You are an expert HR. Use job offer description to create a cover letter, edit a CV.
          ''',
        model="gpt-4o",
        tools=[{"type": "file_search"}],
    )

@app.route('/submit_pdf', methods=['POST'])
def submit_pdf():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"})
    if file and file.filename.endswith('.pdf'):
        timestamp = int(time.time())
        filename = f"CV_{timestamp}.pdf"
        file.save(os.path.join("./data", filename))
        assistant.upload_file(f"./data/{filename}")

        return jsonify({"status": "success", "message": "PDF received", "file_path": file.filename})
    else:
        return jsonify({"status": "error", "message": "Invalid file type"})

@app.route('/submit_json', methods=['POST'])
def submit_json():
    data = request.json
    description = data.get('description')
    expertises = data.get('expertises')
    email = data.get('email')

    assistant.chat()

    # Process the received JSON data
    return jsonify({"status": "success", "message": "JSON received", "data": data})

