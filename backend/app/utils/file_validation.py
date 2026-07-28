import re

import magic

from app.utils.config import settings

ALLOWED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}

MAX_FILENAME_LENGTH = 255

class FileValidationError(Exception):
    pass

def sanitize_filename(filename: str) -> str:
    """Strip any directory components and unsafe characters from a client-supplied filename."""
    base = (filename or "").replace("\\", "/").rsplit("/", 1)[-1]
    base = re.sub(r"[^A-Za-z0-9._-]", "_", base).lstrip(".")
    if not base:
        raise FileValidationError("Invalid filename")
    return base[:MAX_FILENAME_LENGTH]

def validate_file(file_bytes: bytes, filename: str) -> str:
    if len(file_bytes) > settings.max_upload_size_bytes:
        raise FileValidationError(f"File exceeds {settings.max_upload_size_mb}MB limit")

    detected_type = magic.from_buffer(file_bytes, mime=True)
    if detected_type not in ALLOWED_MIME_TYPES:
        raise FileValidationError(f"Unsupported file type: {detected_type}")

    return ALLOWED_MIME_TYPES[detected_type]
