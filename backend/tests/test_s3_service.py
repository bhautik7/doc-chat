from unittest.mock import MagicMock, patch

from app.services import s3_service
from app.utils.config import settings


@patch("app.services.s3_service.s3_client")
def test_upload_file_to_s3_namespaces_key_by_user_and_extension(mock_client):
    s3_key = s3_service.upload_file_to_s3(b"file-bytes", "report.final.pdf", user_id=12)

    assert s3_key.startswith("users/12/documents/")
    assert s3_key.endswith(".pdf")
    mock_client.put_object.assert_called_once_with(
        Bucket=settings.s3_bucket_name,
        Key=s3_key,
        Body=b"file-bytes",
    )


@patch("app.services.s3_service.s3_client")
def test_upload_file_to_s3_generates_unique_keys(mock_client):
    first = s3_service.upload_file_to_s3(b"a", "a.txt", user_id=1)
    second = s3_service.upload_file_to_s3(b"a", "a.txt", user_id=1)

    assert first != second


@patch("app.services.s3_service.s3_client")
def test_delete_file_from_s3_deletes_key(mock_client):
    s3_service.delete_file_from_s3("users/1/documents/abc.txt")

    mock_client.delete_object.assert_called_once_with(
        Bucket=settings.s3_bucket_name, Key="users/1/documents/abc.txt"
    )


@patch("app.services.s3_service.s3_client")
def test_get_file_from_s3_returns_body_bytes(mock_client):
    body = MagicMock()
    body.read.return_value = b"stored-bytes"
    mock_client.get_object.return_value = {"Body": body}

    assert s3_service.get_file_from_s3("users/1/documents/abc.txt") == b"stored-bytes"
    mock_client.get_object.assert_called_once_with(
        Bucket=settings.s3_bucket_name, Key="users/1/documents/abc.txt"
    )
