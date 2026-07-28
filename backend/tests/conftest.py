import os

# Settings are read at import time, so provide defaults before importing the app.
os.environ.setdefault("database_url", "sqlite:///:memory:")
os.environ.setdefault("openai_api_key", "test-openai-key")
os.environ.setdefault("jwt_secret_key", "test-jwt-secret")
os.environ.setdefault("s3_bucket_name", "test-bucket")
os.environ.setdefault("aws_access_key_id", "test-access-key")
os.environ.setdefault("aws_secret_access_key", "test-secret-key")

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database.session import Base, get_db
from app.main import app

# Import models so SQLAlchemy registers tables
from app.models.user import User
from app.models.document import Document
from app.models.chat import ChatSession
from sqlalchemy.pool import StaticPool

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"


engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)

    session = TestSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(client):
    client.post("/auth/register", json={"email": "fixture@example.com", "password": "testpass123"})
    res = client.post(
        "/auth/login",
        data={"username": "fixture@example.com", "password": "testpass123"},
    )
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture(scope="function")
def current_user(db_session, auth_headers):
    return db_session.query(User).filter(User.email == "fixture@example.com").first()