
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
from fpdf import FPDF
import json

load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
uploaded_file = None


sample_json = {
    "title": "Sample PDF Document",
    "sections": [
        {
            "heading": "Introduction",
            "content": "This is an introduction paragraph."
        },
        {
            "heading": "Data Table",
            "table": {
                "columns": ["Name", "Age", "City"],
                "data": [
                    ["Alice", 30, "Wonderland"],
                    ["Bob", 25, "Builderland"]
                ]
            }
        }
    ]
}

assistant = Assistant(
        api_key=getenv("OPENAI_API_KEY"),
        assistant_name="CV assistant",
        instructions='''
            You are an expert HR. Use job offer description to create a cover email, edit a CV.
          ''',
        letter_prompt='''
            Create a cover email tailored to the job description, highlighting the most relevant qualifications from the CV proveded in pdf file.
            IMPORTANT: Respond only with finished cover email text, Take name of sender from CV and dont include subject or recipient email. Email should be under 130 words.
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
        assistant.filepath = f"./data/{filename}"
        assistant.upload_file(assistant.filepath)

        return jsonify({"status": "success", "message": "PDF received", "file_path": file.filename})
    else:
        return jsonify({"status": "error", "message": "Invalid file type"})

@app.route('/submit_json', methods=['POST'])
def submit_json():
    data = request.json
    description = data.get('description')
    expertises = data.get('expertises')
    email = data.get('email')

    # create_pdf_from_json(sample_json)

    response = assistant.generate_letter(description, expertises)
    print(response)
    send_email_with_attachment(email, response, assistant.filepath)

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

def create_pdf_from_json(json_data, pdf_filename="new_cv.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Add title if provided
    if "title" in json_data:
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, txt=json_data["title"], ln=True, align='C')
        pdf.ln(10)

    # Iterate through sections
    for section in json_data.get("sections", []):
        # Add section heading
        if "heading" in section:
            pdf.set_font("Arial", "B", 14)
            pdf.cell(200, 10, txt=section["heading"], ln=True)
            pdf.ln(5)

        # Add content if available
        if "content" in section:
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, txt=section["content"])
            pdf.ln(5)

        # Add image if provided
        if "image" in section:
            try:
                pdf.image(section["image"], w=100)  # Adjust width as needed
                pdf.ln(5)
            except Exception as e:
                print(f"Could not add image {section['image']}: {e}")

        # Add table if provided
        if "table" in section:
            table = section["table"]
            col_width = pdf.w / (len(table["columns"]) + 1)
            pdf.set_font("Arial", "B", 12)

            # Add table header
            for col_name in table["columns"]:
                pdf.cell(col_width, 10, col_name, border=1)
            pdf.ln()

            # Add table rows
            pdf.set_font("Arial", size=12)
            for row in table["data"]:
                for item in row:
                    pdf.cell(col_width, 10, str(item), border=1)
                pdf.ln()
            pdf.ln(5)

    # Save the PDF file
    pdf.output(pdf_filename)
    print(f"PDF saved as {pdf_filename}")