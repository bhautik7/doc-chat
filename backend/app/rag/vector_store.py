import logging

import chromadb
from langchain_chroma import Chroma

from app.rag.embeddings import embedding_model
from app.utils.exceptions import VectorStoreError

logger = logging.getLogger(__name__)

chroma_client = chromadb.PersistentClient(path="./chroma_data")

def get_vector_store(collection_name: str = "documents") -> Chroma:
    return Chroma(
        client=chroma_client,
        collection_name=collection_name,
        embedding_function=embedding_model,
    )

def add_chunks_to_store(document_id: int, user_id: int, chunks: list[str]) -> list[str]:
    store = get_vector_store()
    metadatas = [{"document_id": document_id, "user_id": user_id, "chunk_index": i} for i in range(len(chunks))]
    ids = [f"doc_{document_id}_chunk_{i}" for i in range(len(chunks))]
    try:
        store.add_texts(texts=chunks, metadatas=metadatas, ids=ids)
    except Exception as exc:
        logger.exception("Failed to index %d chunks for document %s", len(chunks), document_id)
        raise VectorStoreError("Failed to index the document for search") from exc
    return ids

def delete_document_chunks(document_id: int) -> None:
    store = get_vector_store()
    try:
        store.delete(where={"document_id": document_id})
    except Exception as exc:
        logger.exception("Failed to delete indexed chunks for document %s", document_id)
        raise VectorStoreError("Failed to delete the indexed document content") from exc
