from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import jwt

from app.database import Base, get_db
from app.main import app

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
Session = sessionmaker(bind=engine, autoflush=False)
Base.metadata.create_all(engine)

def override_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_db

def client_for(user_id=101):
    client = TestClient(app)
    token = jwt.encode({"sub": str(user_id)}, "change-me-in-development", algorithm="HS256")
    client.cookies.set("training_access_token", token)
    return client

def test_full_lifecycle():
    client = client_for()
    template = client.post("/api/v1/labs/templates", json={"name": "SD-WAN Lab", "key": "sdwan"})
    assert template.status_code == 200
    lab = client.post("/api/v1/labs", json={"template_id": template.json()["id"], "name": "Student Lab 1"})
    assert lab.status_code == 200
    lab_id = lab.json()["id"]
    assert lab.json()["state"] == "created"
    assert client.post(f"/api/v1/labs/{lab_id}/provision").json()["lab"]["state"] == "provisioned"
    assert client.post(f"/api/v1/labs/{lab_id}/start").json()["lab"]["state"] == "running"
    assert client.post(f"/api/v1/labs/{lab_id}/stop").json()["lab"]["state"] == "stopped"
    assert client.post(f"/api/v1/labs/{lab_id}/reset").status_code == 200
    assert client.post(f"/api/v1/labs/{lab_id}/release").json()["lab"]["state"] == "released"

def test_access_is_user_scoped():
    owner = client_for(201)
    template = owner.post("/api/v1/labs/templates", json={"name": "Generic Lab", "key": "generic"})
    lab = owner.post("/api/v1/labs", json={"template_id": template.json()["id"], "name": "Owned Lab"})
    other = client_for(202)
    assert other.get(f"/api/v1/labs/{lab.json()['id']}").status_code == 403
