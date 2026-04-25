"""
VedDrishti - PDF Parser for Past Papers
Extracts text from COMP2012 exam PDFs
"""

import pdfplumber
from typing import Optional


def extract_text_from_pdf(file_path: str) -> Optional[str]:
    """
    Extract text from past exam PDFs
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text if text.strip() else None
    except Exception as e:
        print(f"Error: {e}")
        return None
