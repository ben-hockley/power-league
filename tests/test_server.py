from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_login_page():
    response = client.get("/login")
    assert response.status_code == 200
    assert "Login" in response.text

def test_home_redirect():
    response = client.get("/")
    assert response.status_code == 200 or response.status_code == 303