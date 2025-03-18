import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app
from user_model import Role

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

def test_create_role_admin(client, admin_token):
    response = client.post(
        "/roles/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "test_role"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_role"

def test_create_role_unauthorized(client, user_token):
    response = client.post(
        "/roles/",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "test_role"}
    )
    assert response.status_code == 403

def test_list_roles_admin(client, admin_token):
    # Create a role first
    client.post(
        "/roles/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "test_role"}
    )
    
    response = client.get(
        "/roles/",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["roles"]) > 0
    assert any(role["name"] == "test_role" for role in data["roles"])

def test_list_roles_unauthorized(client, user_token):
    response = client.get(
        "/roles/",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403

def test_delete_role_admin(client, admin_token):
    # Create a role first
    create_response = client.post(
        "/roles/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "test_role"}
    )
    role_id = create_response.json()["id"]
    
    response = client.delete(
        f"/roles/{role_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Role deleted successfully"

def test_delete_role_unauthorized(client, user_token):
    response = client.delete(
        "/roles/1",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403

def test_assign_role_admin(client, admin_token):
    # Create a role and a user
    role_response = client.post(
        "/roles/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "test_role"}
    )
    role_id = role_response.json()["id"]
    
    user_response = client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "test123"}
    )
    user_id = user_response.json()["id"]
    
    response = client.post(
        f"/roles/assign/{user_id}/{role_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "assigned to user successfully" in response.json()["message"]

def test_remove_role_admin(client, admin_token):
    # Create a role and assign it to a user first
    role_response = client.post(
        "/roles/",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "test_role"}
    )
    role_id = role_response.json()["id"]
    
    user_response = client.post(
        "/users/register",
        json={"email": "test@example.com", "password": "test123"}
    )
    user_id = user_response.json()["id"]
    
    # Assign role
    client.post(
        f"/roles/assign/{user_id}/{role_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Remove role
    response = client.delete(
        f"/roles/remove/{user_id}/{role_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "removed from user successfully" in response.json()["message"]

def test_cannot_delete_admin_role(client, admin_token):
    # Try to delete admin role
    db = TestingSessionLocal()
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    
    response = client.delete(
        f"/roles/{admin_role.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 400
    assert "Cannot delete built-in roles" in response.json()["detail"] 