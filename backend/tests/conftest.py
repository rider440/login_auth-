import uuid
import pytest
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# ─── In-Memory SQLite for Isolated Tests ──────────────────────────────────────
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="function")
def faker():
    """Fresh Faker instance per test to avoid unique-value conflicts."""
    return Faker()


def unique_phone():
    """Generate a truly unique 10-digit phone using UUID to avoid any collision."""
    return str(uuid.uuid4().int)[:10]


@pytest.fixture(scope="function")
def db():
    """Creates fresh tables before each test and drops them after."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """FastAPI TestClient wired to the in-memory test database."""
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def admin_token(client):
    """Register a fresh admin user with a unique phone per test, return JWT."""
    phone = unique_phone()
    client.post("/register", json={"phone": phone, "name": "Test Admin Co."})

    from app.auth import create_access_token
    token = create_access_token(data={"sub": phone, "role": "admin"})
    return token


@pytest.fixture(scope="function")
def auth_client(client, admin_token):
    """Authenticated TestClient with admin Bearer token."""
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {admin_token}"
    }
    return client
