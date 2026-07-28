import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate


def test_user_create_accepts_valid_credentials():
    user = UserCreate(email="valid@example.com", password="testpass123")

    assert user.email == "valid@example.com"


def test_user_create_rejects_short_password():
    with pytest.raises(ValidationError, match="at least 8 characters"):
        UserCreate(email="valid@example.com", password="short")


def test_user_create_rejects_password_over_bcrypt_byte_limit():
    with pytest.raises(ValidationError, match="72 bytes"):
        UserCreate(email="valid@example.com", password="é" * 40)


def test_user_create_rejects_invalid_email():
    with pytest.raises(ValidationError):
        UserCreate(email="not-an-email", password="testpass123")
