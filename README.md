# CV Bot

## Overview

The CV Bot is a Flask-based web application that assists users in generating tailored cover emails for job applications. The bot receives a job description, contact email, and CV from a Google Chrome extension, processes the information using OpenAI's GPT-4 model, and sends a reply to the job offer from your personal email.

## Features

- Upload a CV in PDF format.
- Submit job descriptions and required expertises in JSON format.
- Generate a tailored cover email based on the job description and CV.
- Send the generated cover email along with the CV as an attachment to the specified contact email.

## Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/cv-bot.git
    cd cv-bot
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file in the root directory and add your OpenAI API key and Gmail credentials:
    ```env
    OPENAI_API_KEY=your_openai_api_key
    GMAIL_KEY=your_gmail_app_password
    ```

4. Run the Flask application:
    ```bash
    python main.py
    ```

## API Endpoints

### `/submit_pdf`

- **Method:** POST
- **Description:** Upload a CV in PDF format.
- **Request:**
    - `file`: The PDF file of the CV.
- **Response:**
    - `status`: "success" or "error"
    - `message`: Details about the operation.
    - `file_path`: The path of the uploaded file (if successful).

### `/submit_json`

- **Method:** POST
- **Description:** Submit job descriptions and required expertises in JSON format.
- **Request:**
    - `description`: The job description.
    - `expertises`: The required expertises.
    - `email`: The contact email to send the cover email.
- **Response:**
    - `status`: "success" or "error"
    - `message`: Details about the operation.
    - `data`: The received JSON data.

## Usage

1. Upload a CV in PDF format using the `/submit_pdf` endpoint.
2. Submit the job description, required expertises, and contact email using the `/submit_json` endpoint.
3. The bot will generate a tailored cover email and send it along with the CV to the specified contact email.
