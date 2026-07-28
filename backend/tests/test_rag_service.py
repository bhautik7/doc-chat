import json
from unittest.mock import MagicMock, patch

from app.models.chat import ChatSession, Message
from app.services.rag_service import ask_question


def make_chunk(document_id: int, chunk_index: int, content: str):
    doc = MagicMock()
    doc.page_content = content
    doc.metadata = {"document_id": document_id, "chunk_index": chunk_index}
    return doc


def create_session(db_session, owner_id: int = 1) -> ChatSession:
    session = ChatSession(owner_id=owner_id)
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)
    return session


@patch("app.services.rag_service.generate_answer")
@patch("app.services.rag_service.retrieve_relevant_chunks")
def test_ask_question_returns_answer_with_sources(mock_retrieve, mock_generate, db_session):
    chat_session = create_session(db_session)
    mock_retrieve.return_value = [
        (make_chunk(7, 0, "Refunds are issued within 30 days."), 0.12),
        (make_chunk(9, 3, "Shipping takes 5 days."), 0.44),
    ]
    mock_generate.return_value = "Refunds take 30 days."

    message = ask_question(db_session, user_id=1, session_id=chat_session.id, question="Refund policy?")

    mock_generate.assert_called_once_with(
        "Refund policy?", ["Refunds are issued within 30 days.", "Shipping takes 5 days."]
    )
    assert message.role == "assistant"
    assert message.content == "Refunds take 30 days."
    assert json.loads(message.sources) == [
        {"document_id": 7, "chunk_index": 0, "score": 0.12},
        {"document_id": 9, "chunk_index": 3, "score": 0.44},
    ]


@patch("app.services.rag_service.generate_answer")
@patch("app.services.rag_service.retrieve_relevant_chunks")
def test_ask_question_persists_user_and_assistant_messages(mock_retrieve, mock_generate, db_session):
    chat_session = create_session(db_session)
    mock_retrieve.return_value = [(make_chunk(1, 0, "context"), 0.5)]
    mock_generate.return_value = "answer"

    ask_question(db_session, user_id=1, session_id=chat_session.id, question="question?")

    messages = db_session.query(Message).filter(Message.session_id == chat_session.id).all()
    assert [(m.role, m.content) for m in messages] == [
        ("user", "question?"),
        ("assistant", "answer"),
    ]


@patch("app.services.rag_service.generate_answer")
@patch("app.services.rag_service.retrieve_relevant_chunks", return_value=[])
def test_ask_question_without_matches_skips_llm_call(mock_retrieve, mock_generate, db_session):
    chat_session = create_session(db_session)

    message = ask_question(db_session, user_id=1, session_id=chat_session.id, question="Anything?")

    mock_generate.assert_not_called()
    assert "couldn't find any relevant information" in message.content
    assert json.loads(message.sources) == []


@patch("app.services.rag_service.generate_answer", return_value="answer")
@patch("app.services.rag_service.retrieve_relevant_chunks")
def test_ask_question_forwards_document_filter(mock_retrieve, mock_generate, db_session):
    chat_session = create_session(db_session)
    mock_retrieve.return_value = [(make_chunk(4, 1, "context"), 0.2)]

    ask_question(
        db_session,
        user_id=3,
        session_id=chat_session.id,
        question="question?",
        document_ids=[4, 5],
    )

    mock_retrieve.assert_called_once_with("question?", 3, [4, 5])
