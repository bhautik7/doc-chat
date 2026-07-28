from unittest.mock import MagicMock, patch

from app.rag.vector_store import add_chunks_to_store, delete_document_chunks, get_vector_store


@patch("app.rag.vector_store.Chroma")
def test_get_vector_store_uses_shared_client_and_embedding_model(mock_chroma):
    store = get_vector_store()

    assert store is mock_chroma.return_value
    kwargs = mock_chroma.call_args.kwargs
    assert kwargs["collection_name"] == "documents"
    assert kwargs["embedding_function"] is not None


@patch("app.rag.vector_store.Chroma")
def test_get_vector_store_accepts_custom_collection(mock_chroma):
    get_vector_store("other")

    assert mock_chroma.call_args.kwargs["collection_name"] == "other"


@patch("app.rag.vector_store.get_vector_store")
def test_add_chunks_to_store_tags_chunks_with_owner_and_index(mock_get_store):
    store = MagicMock()
    mock_get_store.return_value = store

    ids = add_chunks_to_store(document_id=5, user_id=3, chunks=["one", "two"])

    assert ids == ["doc_5_chunk_0", "doc_5_chunk_1"]
    store.add_texts.assert_called_once_with(
        texts=["one", "two"],
        metadatas=[
            {"document_id": 5, "user_id": 3, "chunk_index": 0},
            {"document_id": 5, "user_id": 3, "chunk_index": 1},
        ],
        ids=["doc_5_chunk_0", "doc_5_chunk_1"],
    )


@patch("app.rag.vector_store.get_vector_store")
def test_add_chunks_to_store_handles_empty_chunk_list(mock_get_store):
    store = MagicMock()
    mock_get_store.return_value = store

    assert add_chunks_to_store(document_id=1, user_id=1, chunks=[]) == []
    store.add_texts.assert_called_once_with(texts=[], metadatas=[], ids=[])


@patch("app.rag.vector_store.get_vector_store")
def test_delete_document_chunks_filters_by_document_id(mock_get_store):
    store = MagicMock()
    mock_get_store.return_value = store

    delete_document_chunks(document_id=8)

    store.delete.assert_called_once_with(where={"document_id": 8})
