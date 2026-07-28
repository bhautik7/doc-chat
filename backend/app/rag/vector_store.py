import chromadb
from app.rag.embeddings import embedding_model
from langchain_chroma import Chroma

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
    store.add_texts(texts=chunks, metadatas=metadatas, ids=ids)
    return ids

def delete_document_chunks(document_id: int, user_id: int) -> None:
    store = get_vector_store()
    store.delete(where={"$and": [{"document_id": document_id}, {"user_id": user_id}]})