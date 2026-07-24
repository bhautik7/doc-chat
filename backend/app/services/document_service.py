from sqlalchemy.orm import Session
from app.models.document import Document
from app.services.s3_service import upload_file_to_s3, delete_file_from_s3
from app.utils.file_validation import validate_file, FileValidationError

def create_document(db: Session, user_id: int, filename: str, file_bytes: bytes) -> Document:
    file_type = validate_file(file_bytes, filename)   # raises FileValidationError if invalid
    s3_key = upload_file_to_s3(file_bytes, filename, user_id)

    document = Document(
        owner_id=user_id,
        filename=filename,
        file_type=file_type,
        file_size_bytes=len(file_bytes),
        s3_key=s3_key,
        status="uploaded",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    return document

def list_user_documents(db: Session, user_id: int) -> list[Document]:
    return db.query(Document).filter(Document.owner_id == user_id).all()

def delete_document(db: Session, user_id: int, document_id: int) -> bool:
    document = db.query(Document).filter(
        Document.id == document_id, Document.owner_id == user_id
    ).first()
    if not document:
        return False
    delete_file_from_s3(document.s3_key)
    db.delete(document)
    db.commit()
    return True