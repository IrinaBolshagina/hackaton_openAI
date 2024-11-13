
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.datastructures import FileStorage
import os
from llm import Assistant
from os import getenv
from dotenv import load_dotenv
import time
import smtplib
from email.message import EmailMessage
from email.mime.base import MIMEBase
from email import encoders
import mimetypes

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
#         send_email_with_attachment("dariarch@gmail.com", "Hello, Daria", f"./data/{filename}", )
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

def send_email_with_attachment(to_email, text, file_path, subject="CV for job offer"):
    # Set up the email
    msg = EmailMessage()
    msg['From'] = 'grigorjan.bigmen@gmail.com'  # Replace with your email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(text)

    # Attach the file
    ctype, encoding = mimetypes.guess_type(file_path)
    if ctype is None or encoding is not None:
        ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)

    with open(file_path, 'rb') as file:
        file_data = file.read()
        file_name = file_path.split('/')[-1]
        msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=file_name)

    # Send the email
    with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Replace with your SMTP server and port
        server.starttls()
        server.login('grigorjan.bigmen@gmail.com', getenv("GMAIL_KEY"))  # Replace with your login credentials
        server.send_message(msg)
    print(f'Email sent to {to_email} with attachment {file_name}')
