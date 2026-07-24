from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.authentication.dependencies import get_current_user
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.document_service import create_document, list_user_documents, delete_document
from app.utils.file_validation import FileValidationError

router = APIRouter(prefix="/documents", tags=["documents"])

@router.post("/upload", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    file_bytes = await file.read()
    try:
        return create_document(db, current_user.id, file.filename, file_bytes)
    except FileValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=list[DocumentResponse])
def get_documents(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return list_user_documents(db, current_user.id)

@router.delete("/{document_id}", status_code=204)
def remove_document(document_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted = delete_document(db, current_user.id, document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")