from pydantic import BaseModel, EmailStr, field_validator

from app.schemas.base import ORMModel

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Password must not exceed 72 bytes")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(ORMModel):
    id: int
    email: EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
