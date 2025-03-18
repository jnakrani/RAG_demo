import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
import os

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

def test_create_user(client):
    response = client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "password" not in data

def test_create_user_duplicate_email(client):
    # Create first user
    client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    # Try to create user with same email
    response = client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_user(client):
    # Create user
    client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    
    # Login
    response = client.post("/users/token?email=test@example.com&password=password123")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_read_users_me(client):
    # Create user and get token
    client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "password123", "full_name": "Test User"}
    )
    response = client.post("/users/token?email=test@example.com&password=password123")
    token = response.json()["access_token"]
    
    # Get user profile
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"

def test_update_user(client):
    # Create user and get token
    client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    response = client.post("/users/token?email=test@example.com&password=password123")
    token = response.json()["access_token"]
    
    # Update user
    response = client.put(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Updated Name"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"

def test_delete_user(client):
    # Create user and get token
    client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "password123"}
    )
    response = client.post("/users/token?email=test@example.com&password=password123")
    token = response.json()["access_token"]
    
    # Delete user
    response = client.delete(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully" 