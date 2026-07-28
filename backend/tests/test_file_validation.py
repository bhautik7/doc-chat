from unittest.mock import patch

import pytest

from app.utils.file_validation import MAX_FILE_SIZE_BYTES, FileValidationError, validate_file

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def test_validate_file_accepts_txt():
    assert validate_file(b"just some plain text", "notes.txt") == "txt"


@patch("app.utils.file_validation.magic.from_buffer", return_value=DOCX_MIME)
def test_validate_file_accepts_docx(mock_from_buffer):
    assert validate_file(b"PK\x03\x04docx-bytes", "notes.docx") == "docx"


def test_validate_file_accepts_pdf():
    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"

    assert validate_file(pdf_bytes, "notes.pdf") == "pdf"


def test_validate_file_rejects_unsupported_type():
    with pytest.raises(FileValidationError, match="Unsupported file type"):
        validate_file(b"\x89PNG\r\n\x1a\n" + b"\x00" * 32, "image.png")


def test_validate_file_rejects_oversized_file():
    with pytest.raises(FileValidationError, match="20MB limit"):
        validate_file(b"a" * (MAX_FILE_SIZE_BYTES + 1), "big.txt")
