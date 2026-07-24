from pydantic import BaseModel
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_type: str
    file_size_bytes: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True