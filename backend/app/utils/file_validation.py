import magic

from app.utils.exceptions import AppError

ALLOWED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}

MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB

class FileValidationError(AppError):
    status_code = 400
    default_message = "File failed validation"

def validate_file(file_bytes: bytes, filename: str) -> str:
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        raise FileValidationError("File exceeds 20MB limit")

    if not file_bytes:
        raise FileValidationError("Uploaded file is empty")

    try:
        detected_type = magic.from_buffer(file_bytes, mime=True)
    except Exception as exc:
        raise FileValidationError("Could not determine the file type") from exc
    if detected_type not in ALLOWED_MIME_TYPES:
        raise FileValidationError(f"Unsupported file type: {detected_type}")

    return ALLOWED_MIME_TYPES[detected_type]