import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import io
from user_model import User

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
    return io.BytesIO(b"%PDF-1.4\nTest PDF content with some information about AI and machine learning.").getvalue()

@pytest.fixture
def uploaded_document(client, admin_token, sample_pdf):
    # Upload a test document
    files = {"file": ("test.pdf", sample_pdf, "application/pdf")}
    response = client.post(
        "/documents/upload",
        headers={"Authorization": f"Bearer {admin_token}"},
        files=files
    )
    return response.json()["document_id"]

def test_ask_question_user(client, user_token, uploaded_document):
    response = client.post(
        "/qa/ask",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"query": "What is the document about?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data

def test_ask_question_admin(client, admin_token, uploaded_document):
    response = client.post(
        "/qa/ask",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"query": "What is the document about?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "sources" in data

def test_ask_question_unauthorized(client, uploaded_document):
    response = client.post(
        "/qa/ask",
        json={"query": "What is the document about?"}
    )
    assert response.status_code == 401

def test_ask_question_no_documents(client, user_token):
    # Clear any existing documents
    client.delete(
        "/documents/clear",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    
    response = client.post(
        "/qa/ask",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"query": "What is the document about?"}
    )
    assert response.status_code == 500
    assert "Error searching documents" in response.json()["detail"]

def test_get_qa_history_user(client, user_token):
    response = client.get(
        "/qa/history",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200
    assert "history" in response.json()

def test_get_qa_history_admin(client, admin_token):
    response = client.get(
        "/qa/history",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "history" in response.json()

def test_get_qa_history_unauthorized(client):
    response = client.get("/qa/history")
    assert response.status_code == 401 