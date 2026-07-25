import pytest
from app.schemas.user import UserCreate
from app.services.auth_service import register_user, authenticate_user

def test_register_user_creates_user_with_hashed_password(db_session):
    user_data = UserCreate(email="test@example.com", password="testpass123")
    user = register_user(db_session, user_data)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.hashed_password != "testpass123"   # never stored as plaintext

def test_register_user_rejects_duplicate_email(db_session):
    user_data = UserCreate(email="dup@example.com", password="testpass123")
    register_user(db_session, user_data)

    with pytest.raises(ValueError, match="already registered"):
        register_user(db_session, user_data)

def test_authenticate_user_succeeds_with_correct_password(db_session):
    user_data = UserCreate(email="auth@example.com", password="correctpass")
    register_user(db_session, user_data)

    user = authenticate_user(db_session, "auth@example.com", "correctpass")
    assert user is not None

def test_authenticate_user_fails_with_wrong_password(db_session):
    user_data = UserCreate(email="auth2@example.com", password="correctpass")
    register_user(db_session, user_data)

    user = authenticate_user(db_session, "auth2@example.com", "wrongpass")
    assert user is None