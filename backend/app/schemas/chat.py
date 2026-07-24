from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class AskQuestionRequest(BaseModel):
    session_id: int
    question: str
    document_ids: Optional[List[int]] = None

class MessageResponse(BaseModel):
    id: int
    role: str
    content: str
    sources: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True