from app.rag.chunker import chunk_text
from app.rag.text_cleaner import clean_text


def test_clean_text_collapses_excessive_newlines_and_spaces():
    assert clean_text("a\n\n\n\nb   c\t\td") == "a\n\nb c d"


def test_clean_text_preserves_single_blank_line():
    assert clean_text("a\n\nb") == "a\n\nb"


def test_clean_text_strips_null_bytes_and_surrounding_whitespace():
    assert clean_text("  he\x00llo  ") == "hello"


def test_chunk_text_splits_long_text_with_overlap():
    text = " ".join(f"sentence{i}." for i in range(400))

    chunks = chunk_text(text, chunk_size=200, chunk_overlap=50)

    assert len(chunks) > 1
    assert all(len(chunk) <= 200 for chunk in chunks)


def test_chunk_text_keeps_short_text_in_single_chunk():
    assert chunk_text("short text") == ["short text"]
