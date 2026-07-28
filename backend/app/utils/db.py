from typing import Optional, Type, TypeVar

from sqlalchemy.orm import Session

from app.database.session import Base

ModelT = TypeVar("ModelT", bound=Base)


def save(db: Session, instance: ModelT) -> ModelT:
    db.add(instance)
    db.commit()
    db.refresh(instance)
    return instance


def get_owned(db: Session, model: Type[ModelT], owner_id: int, instance_id: int) -> Optional[ModelT]:
    return db.query(model).filter(model.id == instance_id, model.owner_id == owner_id).first()


def list_owned(db: Session, model: Type[ModelT], owner_id: int) -> list[ModelT]:
    return db.query(model).filter(model.owner_id == owner_id).all()
