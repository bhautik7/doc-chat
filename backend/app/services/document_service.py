import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.document import Document
from app.rag.chunker import chunk_text
from app.rag.document_loader import extract_text
from app.rag.text_cleaner import clean_text
from app.rag.vector_store import add_chunks_to_store, delete_document_chunks
from app.services.s3_service import delete_file_from_s3, get_file_from_s3, upload_file_to_s3
from app.utils.exceptions import AppError, DocumentProcessingError, NotFoundError
from app.utils.file_validation import validate_file

logger = logging.getLogger(__name__)


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
    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except SQLAlchemyError:
        db.rollback()
        # The stored object would otherwise be orphaned with no row referencing it.
        _delete_from_s3_best_effort(s3_key)
        raise

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
    delete_document_chunks(document.id)
    delete_file_from_s3(document.s3_key)
    db.delete(document)
    db.commit()
    return True


def process_document(db: Session, document: Document, file_bytes: bytes) -> None:
    try:
        raw_text = extract_text(file_bytes, document.file_type)
        cleaned = clean_text(raw_text)
        chunks = chunk_text(cleaned)
        if not chunks:
            raise DocumentProcessingError(f"No readable text found in '{document.filename}'")
        add_chunks_to_store(document.id, document.owner_id, chunks)
    except Exception as exc:
        logger.exception("Processing failed for document %s", document.id)
        _set_status(db, document, "failed", suppress_errors=True)
        if isinstance(exc, AppError):
            raise
        raise DocumentProcessingError(f"Failed to process '{document.filename}'") from exc

    _set_status(db, document, "ready")


def reprocess_document(db: Session, user_id: int, document_id: int) -> Document:
    document = db.query(Document).filter(
        Document.id == document_id, Document.owner_id == user_id
    ).first()
    if not document:
        raise NotFoundError("Document not found")

    file_bytes = get_file_from_s3(document.s3_key)
    delete_document_chunks(document.id)
    process_document(db, document, file_bytes)
    return document


def _set_status(db: Session, document: Document, status: str, suppress_errors: bool = False) -> None:
    try:
        document.status = status
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Could not persist status '%s' for document %s", status, document.id)
        if not suppress_errors:
            raise


def _delete_from_s3_best_effort(s3_key: str) -> None:
    try:
        delete_file_from_s3(s3_key)
    except AppError:
        logger.exception("Could not clean up orphaned object %s", s3_key)
