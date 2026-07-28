from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.authentication.dependencies import get_current_user
from app.models.user import User
from app.models.chat import ChatSession
from app.schemas.chat import AskQuestionRequest, MessageResponse, ChatSessionResponse
from app.services.rag_service import ask_question
from app.utils.db import get_owned, list_owned, save

router = APIRouter(prefix="/chat", tags=["chat"])


def get_session_or_404(db: Session, user_id: int, session_id: int) -> ChatSession:
    session = get_owned(db, ChatSession, user_id, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session


@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
def create_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return save(db, ChatSession(owner_id=current_user.id))

@router.get("/sessions", response_model=list[ChatSessionResponse])
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_owned(db, ChatSession, current_user.id)

@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
def get_messages(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_session_or_404(db, current_user.id, session_id).messages

@router.post("/ask", response_model=MessageResponse)
def ask(payload: AskQuestionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    get_session_or_404(db, current_user.id, payload.session_id)

    return ask_question(db, current_user.id, payload.session_id, payload.question, payload.document_ids)
