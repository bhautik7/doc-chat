from unittest.mock import patch

import pytest

from app.models.document import Document
from app.services.document_service import (
    create_document,
    delete_document,
    list_user_documents,
    process_document,
    reprocess_document,
)
from app.utils.file_validation import FileValidationError

TXT_BYTES = b"This is a test document about refund policies."


def make_document(db_session, owner_id=1, s3_key="users/1/documents/a.txt", status="uploaded"):
    document = Document(
        owner_id=owner_id,
        filename="a.txt",
        file_type="txt",
        file_size_bytes=len(TXT_BYTES),
        s3_key=s3_key,
        status=status,
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    return document


@patch("app.services.document_service.add_chunks_to_store")
@patch("app.services.document_service.upload_file_to_s3", return_value="users/1/documents/a.txt")
def test_create_document_stores_metadata_and_indexes_chunks(mock_upload, mock_add_chunks, db_session):
    document = create_document(db_session, user_id=1, filename="a.txt", file_bytes=TXT_BYTES)

    assert document.id is not None
    assert document.file_type == "txt"
    assert document.file_size_bytes == len(TXT_BYTES)
    assert document.s3_key == "users/1/documents/a.txt"
    assert document.status == "ready"
    mock_upload.assert_called_once_with(TXT_BYTES, "a.txt", 1)
    document_id, user_id, chunks = mock_add_chunks.call_args.args
    assert (document_id, user_id) == (document.id, 1)
    assert chunks == [TXT_BYTES.decode()]


@patch("app.services.document_service.upload_file_to_s3")
def test_create_document_rejects_unsupported_file_type(mock_upload, db_session):
    with pytest.raises(FileValidationError):
        create_document(db_session, user_id=1, filename="a.bin", file_bytes=b"\x00\x01\x02\x03binary")

    mock_upload.assert_not_called()
    assert db_session.query(Document).count() == 0


def test_list_user_documents_only_returns_owned_documents(db_session):
    make_document(db_session, owner_id=1, s3_key="users/1/documents/a.txt")
    make_document(db_session, owner_id=2, s3_key="users/2/documents/b.txt")

    documents = list_user_documents(db_session, user_id=1)

    assert [d.owner_id for d in documents] == [1]


@patch("app.services.document_service.delete_file_from_s3")
def test_delete_document_removes_row_and_s3_object(mock_delete_s3, db_session):
    document = make_document(db_session)

    assert delete_document(db_session, user_id=1, document_id=document.id) is True
    mock_delete_s3.assert_called_once_with("users/1/documents/a.txt")
    assert db_session.query(Document).count() == 0


@patch("app.services.document_service.delete_file_from_s3")
def test_delete_document_ignores_documents_owned_by_others(mock_delete_s3, db_session):
    document = make_document(db_session, owner_id=2, s3_key="users/2/documents/b.txt")

    assert delete_document(db_session, user_id=1, document_id=document.id) is False
    mock_delete_s3.assert_not_called()
    assert db_session.query(Document).count() == 1


@patch("app.services.document_service.add_chunks_to_store", side_effect=RuntimeError("embedding down"))
def test_process_document_marks_document_failed_and_reraises(mock_add_chunks, db_session):
    document = make_document(db_session)

    with pytest.raises(RuntimeError, match="embedding down"):
        process_document(db_session, document, TXT_BYTES)

    db_session.refresh(document)
    assert document.status == "failed"


@patch("app.services.document_service.add_chunks_to_store")
@patch("app.services.document_service.get_file_from_s3", return_value=TXT_BYTES)
def test_reprocess_document_reindexes_from_s3(mock_get_file, mock_add_chunks, db_session):
    document = make_document(db_session, status="failed")

    reprocessed = reprocess_document(db_session, user_id=1, document_id=document.id)

    mock_get_file.assert_called_once_with("users/1/documents/a.txt")
    mock_add_chunks.assert_called_once()
    assert reprocessed.status == "ready"


@patch("app.services.document_service.get_file_from_s3")
def test_reprocess_document_rejects_unknown_document(mock_get_file, db_session):
    with pytest.raises(ValueError, match="Document not found"):
        reprocess_document(db_session, user_id=1, document_id=404)

    mock_get_file.assert_not_called()
