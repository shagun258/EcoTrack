import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_ecotrack.db")
os.environ.setdefault("JWT_SECRET", "test-secret-for-ci")
os.environ.setdefault("ML_MODE", "demo")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import app.db.session as session_mod

# Point the app at an isolated SQLite file before importing anything that
# creates a SQLAlchemy engine at import time.
test_engine = create_engine("sqlite:///./test_ecotrack.db", connect_args={"check_same_thread": False})
session_mod.engine = test_engine
session_mod.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

import app.models  # noqa: E402  (registers all tables on Base.metadata)
from app.db.session import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _create_tables():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("test_ecotrack.db"):
        os.remove("test_ecotrack.db")


@pytest.fixture()
def db_session():
    session = session_mod.SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    def override_get_db():
        session = session_mod.SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def registered_user(client):
    # Random email per test - the DB is session-scoped across all tests,
    # so reusing a fixed address would collide with the unique constraint.
    import uuid

    email = f"user-{uuid.uuid4().hex[:10]}@example.com"
    payload = {"full_name": "Test User", "email": email, "password": "password123"}
    resp = client.post("/api/auth/register", json=payload)
    assert resp.status_code == 201
    return resp.json()


@pytest.fixture()
def auth_headers(registered_user):
    return {"Authorization": f"Bearer {registered_user['access_token']}"}
