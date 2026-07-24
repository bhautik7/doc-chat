from sqlalchemy.orm import Session
from app.models.document import Document
from app.services.s3_service import upload_file_to_s3, delete_file_from_s3
from app.utils.file_validation import validate_file, FileValidationError
from app.rag.document_loader import extract_text
from app.rag.text_cleaner import clean_text
from app.rag.chunker import chunk_text
from app.rag.vector_store import add_chunks_to_store
from app.services.s3_service import get_file_from_s3


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
    process_document(db, document, file_bytes)
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


def process_document(db: Session, document: Document, file_bytes: bytes) -> None:
    try:
        raw_text = extract_text(file_bytes, document.file_type)
        cleaned = clean_text(raw_text)
        chunks = chunk_text(cleaned)
        add_chunks_to_store(document.id, document.owner_id, chunks)

        document.status = "ready"
    except Exception:
        document.status = "failed"
        raise
    finally:
        db.commit()
        


def reprocess_document(db: Session, user_id: int, document_id: int) -> Document:
    document = db.query(Document).filter(
        Document.id == document_id, Document.owner_id == user_id
    ).first()
    if not document:
        raise ValueError("Document not found")

    file_bytes = get_file_from_s3(document.s3_key)
    process_document(db, document, file_bytes)
    return document