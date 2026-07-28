import pytest
from unittest.mock import patch

from botocore.exceptions import ClientError

from app.models.document import Document
from app.services.document_service import create_document, process_document
from app.utils.exceptions import DocumentProcessingError, StorageError
from app.services.s3_service import delete_file_from_s3, upload_file_to_s3


def get_auth_headers(client, email="errors@example.com"):
    client.post("/auth/register", json={"email": email, "password": "testpass123"})
    res = client.post("/auth/login", data={"username": email, "password": "testpass123"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def client_error(code):
    return ClientError({"Error": {"Code": code, "Message": code}}, "PutObject")


def test_upload_rejects_invalid_file_type(client):
    headers = get_auth_headers(client)
    res = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("evil.exe", b"MZ\x90\x00binary payload", "application/octet-stream")},
    )
    assert res.status_code == 400
    assert "Unsupported file type" in res.json()["detail"]


@patch("app.services.document_service.upload_file_to_s3", side_effect=StorageError())
def test_upload_surfaces_storage_failure(mock_upload, client):
    headers = get_auth_headers(client)
    res = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("test.txt", b"hello world", "text/plain")},
    )
    assert res.status_code == 502
    assert res.json()["detail"] == StorageError.default_message


@patch("app.services.document_service.add_chunks_to_store", side_effect=RuntimeError("chroma down"))
@patch("app.services.document_service.upload_file_to_s3", return_value="fake-s3-key")
def test_upload_reports_processing_failure_and_marks_document_failed(mock_s3, mock_chunks, client, db_session):
    headers = get_auth_headers(client)
    res = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("test.txt", b"a document about refunds", "text/plain")},
    )
    assert res.status_code == 422
    assert "Failed to process 'test.txt'" in res.json()["detail"]
    assert db_session.query(Document).one().status == "failed"


@patch("app.services.document_service.add_chunks_to_store")
def test_process_document_rejects_document_without_text(mock_chunks, db_session):
    document = Document(
        owner_id=1, filename="blank.txt", file_type="txt", file_size_bytes=3, s3_key="k", status="uploaded"
    )
    db_session.add(document)
    db_session.commit()

    with pytest.raises(DocumentProcessingError, match="No readable text"):
        process_document(db_session, document, b"   ")

    mock_chunks.assert_not_called()
    assert document.status == "failed"


@patch("app.services.document_service.delete_file_from_s3")
@patch("app.services.document_service.upload_file_to_s3", return_value="fake-s3-key")
def test_create_document_cleans_up_stored_file_when_row_cannot_be_saved(mock_s3, mock_delete, db_session):
    from sqlalchemy.exc import OperationalError

    with patch.object(db_session, "commit", side_effect=OperationalError("insert", {}, Exception())):
        with pytest.raises(OperationalError):
            create_document(db_session, user_id=1, filename="test.txt", file_bytes=b"hello world")

    mock_delete.assert_called_once_with("fake-s3-key")


@patch("app.services.document_service.delete_document_chunks")
@patch("app.services.document_service.delete_file_from_s3")
@patch("app.services.document_service.add_chunks_to_store")
@patch("app.services.document_service.upload_file_to_s3", return_value="fake-s3-key")
def test_delete_document_removes_indexed_chunks(mock_s3, mock_chunks, mock_delete_s3, mock_delete_chunks, client):
    headers = get_auth_headers(client)
    upload = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("test.txt", b"a document about refunds", "text/plain")},
    )
    document_id = upload.json()["id"]

    res = client.delete(f"/documents/{document_id}", headers=headers)

    assert res.status_code == 204
    mock_delete_chunks.assert_called_once_with(document_id)


@patch("app.services.s3_service.s3_client")
def test_upload_file_to_s3_wraps_client_errors(mock_client):
    mock_client.put_object.side_effect = client_error("AccessDenied")

    with pytest.raises(StorageError):
        upload_file_to_s3(b"data", "test.txt", user_id=1)


@patch("app.services.s3_service.s3_client")
def test_delete_file_from_s3_tolerates_missing_object(mock_client):
    mock_client.delete_object.side_effect = client_error("NoSuchKey")

    delete_file_from_s3("missing-key")


def test_expired_or_malformed_token_is_rejected(client):
    res = client.get("/documents/", headers={"Authorization": "Bearer not-a-jwt"})
    assert res.status_code == 401
