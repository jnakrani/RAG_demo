import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import os
import io

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def admin_token(client):
    # Create admin user
    response = client.post(
        "/users/register",
        json={"email": "admin@example.com", "password": "admin123", "full_name": "Admin User"}
    )
    # Make user admin in database
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "admin@example.com").first()
    user.is_admin = True
    db.commit()
    
    # Get admin token
    response = client.post("/users/token?email=admin@example.com&password=admin123")
    return response.json()["access_token"]

@pytest.fixture
def user_token(client):
    # Create regular user
    response = client.post(
        "/users/register",
        json={"email": "user@example.com", "password": "user123", "full_name": "Regular User"}
    )
    # Get user token
    response = client.post("/users/token?email=user@example.com&password=user123")
    return response.json()["access_token"]

@pytest.fixture
def sample_pdf():
    # Create a simple PDF-like bytes object for testing
    return io.BytesIO(b"%PDF-1.4\nTest PDF content").getvalue()

def test_list_documents_user(client, user_token):
    response = client.get(
        "/documents/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert "documents" in response.json()

def test_list_documents_admin(client, admin_token):
    response = client.get(
        "/documents/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "documents" in response.json()

def test_list_documents_unauthorized(client):
    response = client.get("/documents/")
    assert response.status_code == 401

def test_upload_document_user(client, user_token, sample_pdf):
    files = {"file": ("test.pdf", sample_pdf, "application/pdf")}
    response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {user_token}"},
        files=files
    )
    assert response.status_code == 200
    assert "document_id" in response.json()

def test_upload_document_admin(client, admin_token, sample_pdf):
    files = {"file": ("test.pdf", sample_pdf, "application/pdf")}
    response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {admin_token}"},
        files=files
    )
    assert response.status_code == 200
    assert "document_id" in response.json()

def test_upload_invalid_file(client, user_token):
    files = {"file": ("test.txt", b"Not a PDF", "text/plain")}
    response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {user_token}"},
        files=files
    )
    assert response.status_code == 400
    assert "File must be a PDF" in response.json()["detail"]

def test_delete_document_admin(client, admin_token, sample_pdf):
    # Upload a document first
    files = {"file": ("test.pdf", sample_pdf, "application/pdf")}
    upload_response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {admin_token}"},
        files=files
    )
    document_id = upload_response.json()["document_id"]
    
    # Delete the document
    response = client.delete(
        f"/documents/{document_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "Document deleted successfully" in response.json()["message"]

def test_delete_document_unauthorized(client, user_token, sample_pdf):
    # Upload a document first
    files = {"file": ("test.pdf", sample_pdf, "application/pdf")}
    upload_response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {user_token}"},
        files=files
    )
    document_id = upload_response.json()["document_id"]
    
    # Try to delete the document
    response = client.delete(
        f"/documents/{document_id}",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403

def test_clear_collection_admin(client, admin_token):
    response = client.delete(
        "/documents/clear",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "Collection cleared successfully" in response.json()["message"]

def test_clear_collection_unauthorized(client, user_token):
    response = client.delete(
        "/documents/clear",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403 