import pdfplumber
from docx import Document

def load_document(file_path: str) -> str:
    """Extract text from PDF, DOCX, or TXT."""
    if file_path.endswith(".pdf"):
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    elif file_path.endswith(".docx"):
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    else:  # assume .txt
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()