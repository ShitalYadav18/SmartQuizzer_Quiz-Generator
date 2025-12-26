import pdfplumber
import re
from typing import List

def extract_text_from_pdf(file_path: str) -> str:
    text = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text.append(page_text)
    return "\n".join(text)

def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_into_chunks(text: str, max_tokens: int = 800) -> List[str]:
    words = text.split()
    chunks, current = [], []
    count = 0
    for w in words:
        current.append(w)
        count += 1
        if count >= max_tokens:
            chunks.append(" ".join(current))
            current, count = [], 0
    if current:
        chunks.append(" ".join(current))
    return chunks
