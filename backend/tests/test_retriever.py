from unittest.mock import patch, MagicMock
from app.rag.retriever import retrieve_relevant_chunks

@patch("app.rag.retriever.get_vector_store")
def test_retrieval_filters_by_user_id(mock_get_store):
    mock_store = MagicMock()
    mock_get_store.return_value = mock_store
    mock_store.similarity_search_with_score.return_value = []

    retrieve_relevant_chunks("What is the policy?", user_id=42)

    call_kwargs = mock_store.similarity_search_with_score.call_args.kwargs
    assert call_kwargs["filter"] == {"user_id": 42}