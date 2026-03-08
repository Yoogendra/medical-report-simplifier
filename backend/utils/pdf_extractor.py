import pdfplumber
import logging

def extract_text_from_pdf(path: str) -> str:
    """
    Extracts all text content from a given PDF file path using pdfplumber.

    Args:
        path (str): The local file path to the PDF document.

    Returns:
        str: The fully extracted string content of the PDF. Returns an empty string on failure.
    """
    try:
        with pdfplumber.open(path) as pdf:
            text = ""
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            return text
    except Exception as e:
        logging.error(f"Failed to extract text from PDF: {e}")
        return ""
