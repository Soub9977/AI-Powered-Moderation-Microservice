# tests/test_main.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

# Auth tests
def test_create_user():
    response = client.post(
        "/users/",
        json={"username": "testuser20", "password": "testpass20"}
    )
    assert response.status_code == 201
    assert "username" in response.json()

def test_login():
    # First create user
    client.post(
        "/users/",
        json={"username": "testuser20", "password": "testpass20"}
    )
    
    # Then try to login
    response = client.post(
        "/token",
        data={"username": "testuser20", "password": "testpass20"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

# Comment tests
def test_create_comment():
    # First login
    login_response = client.post(
        "/token",
        data={"username": "testuser20", "password": "testpass20"}
    )
    token = login_response.json()["access_token"]
    
    # Create comment
    response = client.post(
        "/comments/",
        headers={"Authorization": f"Bearer {token}"},
        json={"text": "Test comment"}
    )
    assert response.status_code == 201
    assert response.json()["text"] == "Test comment"