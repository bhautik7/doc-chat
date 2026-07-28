from unittest.mock import patch

from app.utils.config import settings

def get_auth_headers(client):
    client.post("/auth/register", json={"email": "flow@example.com", "password": "testpass123"})
    res = client.post(
        "/auth/login",
        data={"username": "flow@example.com", "password": "testpass123"},
    )
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_upload_document_requires_auth(client):
    res = client.post("/documents/upload", files={"file": ("test.txt", b"hello world", "text/plain")})
    assert res.status_code == 401

@patch("app.services.document_service.add_chunks_to_store")
@patch("app.services.document_service.upload_file_to_s3", return_value="fake-s3-key")
def test_upload_document_succeeds_and_returns_document(mock_s3, mock_chunks, client):
    headers = get_auth_headers(client)
    res = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("test.txt", b"This is a test document about refund policies.", "text/plain")},
    )
    assert res.status_code == 201
    assert res.json()["filename"] == "test.txt"
    assert res.json()["status"] == "ready"

@patch("app.services.document_service.add_chunks_to_store")
@patch("app.services.document_service.upload_file_to_s3", return_value="fake-s3-key")
def test_upload_document_sanitizes_filename(mock_s3, mock_chunks, client):
    headers = get_auth_headers(client)
    res = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("../../etc/passwd.txt", b"some plain text content", "text/plain")},
    )
    assert res.status_code == 201
    assert res.json()["filename"] == "passwd.txt"
    assert mock_s3.call_args.args[1] == "txt"

def test_upload_document_rejects_oversized_file(client):
    headers = get_auth_headers(client)
    oversized = b"a" * (settings.max_upload_size_bytes + 1)
    res = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("big.txt", oversized, "text/plain")},
    )
    assert res.status_code == 413