from unittest.mock import patch

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

@patch("app.services.document_service.upload_file_to_s3")
def test_upload_document_rejects_unsupported_file_type(mock_s3, client):
    headers = get_auth_headers(client)
    res = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("image.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 32, "image/png")},
    )
    assert res.status_code == 400
    assert "Unsupported file type" in res.json()["detail"]

def test_list_documents_requires_auth(client):
    assert client.get("/documents/").status_code == 401

@patch("app.services.document_service.add_chunks_to_store")
@patch("app.services.document_service.upload_file_to_s3", return_value="fake-s3-key")
def test_list_documents_returns_uploaded_documents(mock_s3, mock_chunks, client):
    headers = get_auth_headers(client)
    client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("test.txt", b"This is a test document about refund policies.", "text/plain")},
    )

    res = client.get("/documents/", headers=headers)

    assert res.status_code == 200
    assert [d["filename"] for d in res.json()] == ["test.txt"]

@patch("app.services.document_service.delete_file_from_s3")
@patch("app.services.document_service.add_chunks_to_store")
@patch("app.services.document_service.upload_file_to_s3", return_value="fake-s3-key")
def test_delete_document_removes_document(mock_s3, mock_chunks, mock_delete, client):
    headers = get_auth_headers(client)
    document_id = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("test.txt", b"This is a test document about refund policies.", "text/plain")},
    ).json()["id"]

    res = client.delete(f"/documents/{document_id}", headers=headers)

    assert res.status_code == 204
    assert client.get("/documents/", headers=headers).json() == []

def test_delete_document_returns_404_for_unknown_document(client):
    headers = get_auth_headers(client)

    res = client.delete("/documents/999", headers=headers)

    assert res.status_code == 404
    assert res.json()["detail"] == "Document not found"

@patch("app.services.document_service.get_file_from_s3", return_value=b"Reprocessed document text.")
@patch("app.services.document_service.add_chunks_to_store")
@patch("app.services.document_service.upload_file_to_s3", return_value="fake-s3-key")
def test_reprocess_document_returns_ready_document(mock_s3, mock_chunks, mock_get_file, client):
    headers = get_auth_headers(client)
    document_id = client.post(
        "/documents/upload",
        headers=headers,
        files={"file": ("test.txt", b"This is a test document about refund policies.", "text/plain")},
    ).json()["id"]

    res = client.post(f"/documents/{document_id}/reprocess", headers=headers)

    assert res.status_code == 200
    assert res.json()["status"] == "ready"
    mock_get_file.assert_called_once_with("fake-s3-key")

def test_reprocess_document_returns_404_for_unknown_document(client):
    headers = get_auth_headers(client)

    res = client.post("/documents/999/reprocess", headers=headers)

    assert res.status_code == 404
    assert res.json()["detail"] == "Document not found"