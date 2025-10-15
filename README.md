Credit Card Statement Parser
Introduction

This project is a Credit Card Statement Parser that extracts key information from credit card statements in PDF format. It works with both text-based PDFs and scanned images using OCR. The parser generates a summary PDF containing essential details like cardholder name, statement period, card number, total due, minimum due, and credit limit.

It is designed to handle different terminologies and formats used in various credit card statements.

How It Works

File Upload: Users upload a PDF credit card statement through the frontend.

Text Extraction: The backend first tries to extract text using pdfplumber. If the PDF is scanned, it falls back to OCR via pytesseract.

Data Parsing: The extracted text is scanned line by line using semantic term mapping, identifying key fields such as:

Cardholder Name

Statement Start & End Dates

Statement Date

Total Due Amount

Minimum Due Amount

Card Number (masked)

Credit Limit

Summary Generation: The parsed data is used to generate a summary PDF using ReportLab.

Download: The summary PDF is sent back to the user for download.

Project Structure
SURE/
│
├── backend/
│   ├── backend.js           ← Node.js server for file uploads
│   ├── package.json
│   └── package-lock.json
│
├── nlp_service/
│   ├── app.py               ← Flask parser service
│   └── requirements.txt
│
├── frontend/
│   └── index.html           ← Upload page
│
├── run_all.bat              ← Optional script to run backend + Flask
└── README.md                ← Project documentation

Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/rishisingh9152-cyber/parser.git
cd parser

2️⃣ Backend (Node.js)
cd backend
npm install
node backend.js


Runs the Node.js server on http://localhost:5000.

3️⃣ NLP Service (Python)
cd ../nlp_service
pip install -r requirements.txt
python app.py


Runs the Flask parser on http://localhost:8000.

4️⃣ Frontend

Open frontend/index.html in a browser to access the upload page.

Usage

Open the frontend page in a browser.

Upload your credit card PDF.

The parser extracts relevant information and automatically downloads a summary PDF.
