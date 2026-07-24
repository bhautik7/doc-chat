from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.authentication.dependencies import get_current_user
from app.models.user import User
from app.models.chat import ChatSession, Message
from app.schemas.chat import AskQuestionRequest, MessageResponse, ChatSessionResponse
from app.services.rag_service import ask_question

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
def create_session(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = ChatSession(owner_id=current_user.id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.get("/sessions", response_model=list[ChatSessionResponse])
def list_sessions(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ChatSession).filter(ChatSession.owner_id == current_user.id).all()

@router.get("/sessions/{session_id}/messages", response_model=list[MessageResponse])
def get_messages(session_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id, ChatSession.owner_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return session.messages

@router.post("/ask", response_model=MessageResponse)
def ask(payload: AskQuestionRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    session = db.query(ChatSession).filter(
        ChatSession.id == payload.session_id, ChatSession.owner_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    return ask_question(db, current_user.id, payload.session_id, payload.question, payload.document_ids)