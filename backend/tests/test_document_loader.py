import io
from unittest.mock import MagicMock, patch

import pytest
from docx import Document as DocxDocument

from app.rag.document_loader import extract_text


def make_docx_bytes(paragraphs: list[str]) -> bytes:
    document = DocxDocument()
    for paragraph in paragraphs:
        document.add_paragraph(paragraph)
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def test_extract_text_decodes_txt():
    assert extract_text(b"plain text body", "txt") == "plain text body"


def test_extract_text_ignores_undecodable_txt_bytes():
    assert extract_text(b"caf\xe9 latte", "txt") == "caf latte"


def test_extract_text_reads_docx_paragraphs():
    file_bytes = make_docx_bytes(["First paragraph", "Second paragraph"])

    assert extract_text(file_bytes, "docx") == "First paragraph\nSecond paragraph"


@patch("app.rag.document_loader.PdfReader")
def test_extract_text_joins_pdf_pages(mock_reader):
    page_one = MagicMock()
    page_one.extract_text.return_value = "page one"
    page_two = MagicMock()
    page_two.extract_text.return_value = "page two"
    mock_reader.return_value.pages = [page_one, page_two]

    assert extract_text(b"%PDF-fake", "pdf") == "page one\npage two"


@patch("app.rag.document_loader.PdfReader")
def test_extract_text_treats_unextractable_pdf_pages_as_empty(mock_reader):
    page = MagicMock()
    page.extract_text.return_value = None
    mock_reader.return_value.pages = [page]

    assert extract_text(b"%PDF-fake", "pdf") == ""


def test_extract_text_rejects_unsupported_file_type():
    with pytest.raises(ValueError, match="Unsupported file type: csv"):
        extract_text(b"a,b,c", "csv")
