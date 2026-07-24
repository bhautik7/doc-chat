from langchain_openai import OpenAIEmbeddings
from app.utils.config import settings

embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
    api_key=settings.openai_api_key,
)

def embed_chunks(chunks: list[str]) -> list[list[float]]:
    return embedding_model.embed_documents(chunks)

def embed_query(query: str) -> list[float]:
    return embedding_model.embed_query(query)