from pypdf import PdfReader
from docx import Document as DocxDocument
import io

def extract_text(file_bytes: bytes, file_type: str) -> str:
    if file_type == "pdf":
        return _extract_pdf_text(file_bytes)
    elif file_type == "docx":
        return _extract_docx_text(file_bytes)
    elif file_type == "txt":
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def _extract_pdf_text(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text_parts = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(text_parts)

def _extract_docx_text(file_bytes: bytes) -> str:
    doc = DocxDocument(io.BytesIO(file_bytes))
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)