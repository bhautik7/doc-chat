import magic

ALLOWED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB

class FileValidationError(Exception):
    pass

def validate_file(file_bytes: bytes, filename: str) -> str:
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise FileValidationError("File exceeds 20MB limit")

    detected_type = magic.from_buffer(file_bytes, mime=True)
    if detected_type not in ALLOWED_MIME_TYPES:
        raise FileValidationError(f"Unsupported file type: {detected_type}")

    return ALLOWED_MIME_TYPES[detected_type]