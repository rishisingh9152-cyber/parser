from flask import Flask, request, send_file, jsonify, send_from_directory
import pdfplumber, re, os
from pdf2image import convert_from_path
import pytesseract
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Semantic mapping of bank terms
BANK_TERMS = {
    "card_holder": ["Cardholder", "Card Holder Name", "Customer Name", "Account Holder"],
    "statement_period": ["Statement Period", "Billing Period", "Period", "Statement Cycle"],
    "statement_date": ["Statement Date", "Billing Date", "Date"],
    "total_due": ["Total Due", "Amount Due", "Outstanding Balance", "Total Amount Due", "New Balance"],
    "minimum_due": ["Minimum Due", "Min Amount Due", "Minimum Payment"],
    "card_number": ["Account", "Card Number", "Card No.", "Account Number"],
    "credit_limit": ["Credit Limit", "Available Limit", "Card Limit"]
}

def extract_text_with_ocr(pdf_path):
    """OCR extraction for scanned PDFs"""
    text = ""
    try:
        images = convert_from_path(pdf_path)
        for img in images:
            text += pytesseract.image_to_string(img)
    except Exception as e:
        print("⚠️ OCR failed:", e)
    return text

def extract_text(pdf_path):
    """Extract text using pdfplumber, fallback to OCR"""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
    except Exception as e:
        print("⚠️ PDF extraction failed:", e)

    if len(text.strip()) < 50:
        print("📸 Using OCR fallback...")
        text = extract_text_with_ocr(pdf_path)

    # Normalize text
    text = text.replace("\r", "\n")
    text = "\n".join([line.strip() for line in text.split("\n") if line.strip()])
    return text

def mask_card_number(card_number):
    """Keep only last 4 digits, mask rest"""
    digits = re.sub(r"\D", "", card_number)
    if len(digits) >= 4:
        return "XXXX-XXXX-XXXX-" + digits[-4:]
    return card_number

def extract_dates(line):
    """Extract date in DD MMM YYYY, YYYY-MM-DD, or DD/MM/YYYY"""
    match = re.search(r"(\d{1,2}[-/ ]\w{3}[-/ ]\d{4}|\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", line)
    return match.group(1).strip() if match else None

def extract_info(text):
    """Parse text line-by-line using semantic bank-term mapping"""
    extracted = {
        "Card Holder Name": "Not Found",
        "Statement Start Date": "Not Found",
        "Statement End Date": "Not Found",
        "Statement Date": "Not Found",
        "Minimum Due Amount": "Not Found",
        "Total Due Amount": "Not Found",
        "Card Number": "Not Found",
        "Credit Limit": "Not Found"
    }

    lines = text.split("\n")
    for line in lines:
        line_lower = line.lower()

        # Card holder
        if any(label.lower() in line_lower for label in BANK_TERMS["card_holder"]):
            match = re.search(r":\s*(.+)", line)
            if match:
                extracted["Card Holder Name"] = match.group(1).strip()

        # Card number in parentheses or after label
        card_num_match = re.search(r"\((X{0,4}[-\d]{4,19})\)|:\s*([X\d\s\-]{4,19})", line)
        if card_num_match:
            number = card_num_match.group(1) or card_num_match.group(2)
            extracted["Card Number"] = mask_card_number(number)

        # Statement period (handles DD MMM YYYY - DD MMM YYYY)
        if any(label.lower() in line_lower for label in BANK_TERMS["statement_period"]):
            match = re.findall(r"(\d{1,2}[-/ ]\w{3}[-/ ]\d{4}|\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})", line)
            if len(match) >= 2:
                extracted["Statement Start Date"] = match[0].strip()
                extracted["Statement End Date"] = match[1].strip()

        # Statement date
        if any(label.lower() in line_lower for label in BANK_TERMS["statement_date"]):
            date_val = extract_dates(line)
            if date_val:
                extracted["Statement Date"] = date_val

        # Total due
        if any(label.lower() in line_lower for label in BANK_TERMS["total_due"]):
            match = re.search(r"(?:INR|₹)?\s*([\d,]+\.\d{2})", line, re.IGNORECASE)
            if match:
                extracted["Total Due Amount"] = match.group(1).strip()

        # Minimum due
        if any(label.lower() in line_lower for label in BANK_TERMS["minimum_due"]):
            match = re.search(r"(?:INR|₹)?\s*([\d,]+\.\d{2})", line, re.IGNORECASE)
            if match:
                extracted["Minimum Due Amount"] = match.group(1).strip()

        # Credit limit
        if any(label.lower() in line_lower for label in BANK_TERMS["credit_limit"]):
            match = re.search(r"(?:INR|₹)?\s*([\d,]+\.\d{2})", line, re.IGNORECASE)
            if match:
                extracted["Credit Limit"] = match.group(1).strip()

    return extracted

def generate_output_pdf(data, output_path="summary.pdf"):
    """Generate summary PDF"""
    c = canvas.Canvas(output_path, pagesize=letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(120, 750, "Credit Card Statement Summary")

    c.setFont("Helvetica", 12)
    y = 700
    for key, value in data.items():
        c.drawString(100, y, f"{key}: {value}")
        y -= 25

    c.save()
    return output_path

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/parse", methods=["POST"])
def parse_pdf():
    if "pdf" not in request.files:
        return jsonify({"error": "No PDF uploaded"}), 400

    pdf_file = request.files["pdf"]
    temp_path = f"temp_{pdf_file.filename}"
    pdf_file.save(temp_path)

    text = extract_text(temp_path)
    data = extract_info(text)
    output_pdf = generate_output_pdf(data)

    os.remove(temp_path)
    return send_file(output_pdf, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

