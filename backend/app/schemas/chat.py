from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

MAX_QUESTION_LENGTH = 4000
MAX_DOCUMENT_IDS = 50

class AskQuestionRequest(BaseModel):
    session_id: int
    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)
    document_ids: Optional[List[int]] = Field(default=None, max_length=MAX_DOCUMENT_IDS)

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