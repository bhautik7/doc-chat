import json
from sqlalchemy.orm import Session
from app.models.chat import Message
from app.rag.retriever import retrieve_relevant_chunks
from app.rag.llm import generate_answer
from typing import List, Optional

def ask_question(
    db: Session,
    user_id: int,
    session_id: int,
    question: str,
    document_ids: Optional[List[int]] = None
) -> Message:
    results = retrieve_relevant_chunks(question, user_id, document_ids)
    context_chunks = [doc.page_content for doc, score in results]

    if not context_chunks:
        answer = "I couldn't find any relevant information in your documents to answer this question."
        sources = []
    else:
        answer = generate_answer(question, context_chunks)
        sources = [
            {"document_id": doc.metadata["document_id"], "chunk_index": doc.metadata["chunk_index"], "score": float(score)}
            for doc, score in results
        ]

    user_message = Message(session_id=session_id, role="user", content=question)
    assistant_message = Message(
        session_id=session_id, role="assistant", content=answer, sources=json.dumps(sources)
    )
    db.add_all([user_message, assistant_message])
    db.commit()
    db.refresh(assistant_message)
    return assistant_message