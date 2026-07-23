from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.authentication.hashing import hash_password, verify_password
from app.authentication.jwt_handler import create_access_token
from typing import Optional


def register_user(db: Session, user_data: UserCreate) -> User:
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise ValueError("Email already registered")
    new_user = User(email=user_data.email, hashed_password=hash_password(user_data.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user