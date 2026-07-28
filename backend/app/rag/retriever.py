import logging

from app.rag.vector_store import get_vector_store
from app.utils.exceptions import VectorStoreError
from typing import Optional,List

logger = logging.getLogger(__name__)

def retrieve_relevant_chunks(
    query: str,
    user_id: int,
    document_ids: Optional[List[int]] = None,
    k: int = 4,
):
    store = get_vector_store()

    filter_dict = {"user_id": user_id}
    if document_ids:
        filter_dict = {"$and": [{"user_id": user_id}, {"document_id": {"$in": document_ids}}]}

    try:
        results = store.similarity_search_with_score(query, k=k, filter=filter_dict)
    except Exception as exc:
        logger.exception("Similarity search failed for user %s", user_id)
        raise VectorStoreError("Could not search your documents right now") from exc
    return results   # list of (Document, score) tuples