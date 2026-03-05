from PyPDF2 import PdfReader


def extract_text_from_pdf(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    if not text.strip():
        raise ValueError("Unable to extract text from PDF.")

    return text