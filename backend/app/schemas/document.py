from datetime import datetime

from app.schemas.base import ORMModel


class DocumentResponse(ORMModel):
    id: int
    filename: str
    file_type: str
    file_size_bytes: int
    status: str
    created_at: datetime
