from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/register", json={
        "username": "testuser101",
        "email": "testuser101@example.com",
        "password": "testpass111"
    })
    assert response.status_code in [200, 400]

def test_login_user():
    response = client.post("/token", data={
        "username": "testuser101",
        "password": "testpass111"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_post_comment():
    login = client.post("/token", data={
        "username": "testuser101",
        "password": "testpass111"
    })
    token = login.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/comments/", json={
        "content": "This is a clean comment"
    }, headers=headers)

    assert response.status_code in [200, 400]
