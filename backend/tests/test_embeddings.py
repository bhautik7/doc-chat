from unittest.mock import patch

from app.rag import embeddings


def test_embedding_model_uses_configured_model_name():
    assert embeddings.embedding_model.model == "text-embedding-3-large"


@patch("app.rag.embeddings.embedding_model")
def test_embed_chunks_delegates_to_model(mock_model):
    mock_model.embed_documents.return_value = [[0.1, 0.2], [0.3, 0.4]]

    assert embeddings.embed_chunks(["a", "b"]) == [[0.1, 0.2], [0.3, 0.4]]
    mock_model.embed_documents.assert_called_once_with(["a", "b"])


@patch("app.rag.embeddings.embedding_model")
def test_embed_query_delegates_to_model(mock_model):
    mock_model.embed_query.return_value = [0.5, 0.6]

    assert embeddings.embed_query("question?") == [0.5, 0.6]
    mock_model.embed_query.assert_called_once_with("question?")
