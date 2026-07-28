import io
import logging

from docx import Document as DocxDocument
from pypdf import PdfReader
from pypdf.errors import PyPdfError

from app.utils.exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)

def extract_text(file_bytes: bytes, file_type: str) -> str:
    if file_type == "pdf":
        return _extract_pdf_text(file_bytes)
    elif file_type == "docx":
        return _extract_docx_text(file_bytes)
    elif file_type == "txt":
        return _extract_plain_text(file_bytes)
    else:
        raise DocumentProcessingError(f"Unsupported file type: {file_type}")

def _extract_pdf_text(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text_parts = [page.extract_text() or "" for page in reader.pages]
    except PyPdfError as exc:
        raise DocumentProcessingError("The PDF is corrupt or could not be read") from exc
    return "\n".join(text_parts)

def _extract_docx_text(file_bytes: bytes) -> str:
    try:
        doc = DocxDocument(io.BytesIO(file_bytes))
    except Exception as exc:
        raise DocumentProcessingError("The DOCX file is corrupt or could not be read") from exc
    return "\n".join(paragraph.text for paragraph in doc.paragraphs)

def _extract_plain_text(file_bytes: bytes) -> str:
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        logger.warning("Text file is not valid UTF-8; decoding with replacement characters")
        return file_bytes.decode("utf-8", errors="replace")
