import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import hash_password
from app.main import app
from app.models import Membership, Organization, User

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def platform_admin(client):
    user = User(
        email="course-admin@example.com",
        full_name="Course Admin",
        hashed_password=hash_password("StrongPassword123!"),
        is_platform_admin=True,
    )
    with TestingSessionLocal() as db:
        db.add(user)
        db.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "course-admin@example.com", "password": "StrongPassword123!"},
    )
    assert login.status_code == 200
    return client
