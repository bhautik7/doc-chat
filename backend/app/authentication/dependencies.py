# Auth dependency for protected routes
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.authentication.jwt_handler import decode_access_token
from app.models.user import User

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token:str = Depends(oauth2_scheme),db:Session=Depends(get_db))->User:
    credentials_exception=HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload=decode_access_token(token)
    
    if payload is None:
        raise credentials_exception
    user_id=payload.get("sub")
    if user_id is None:
        raise credentials_exception
    try:
        user_pk = int(user_id)
    except (TypeError, ValueError):
        logger.warning("Token carried a non-numeric subject: %r", user_id)
        raise credentials_exception
    user=db.query(User).filter(User.id == user_pk).first()
    if user is None:
        raise credentials_exception
    return user

