from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.base import ORMModel


class AskQuestionRequest(BaseModel):
    session_id: int
    question: str
    document_ids: Optional[List[int]] = None


class MessageResponse(ORMModel):
    id: int
    role: str
    content: str
    sources: Optional[str]
    created_at: datetime


class ChatSessionResponse(ORMModel):
    id: int
    title: str
    created_at: datetime
