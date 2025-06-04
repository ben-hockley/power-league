import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from routers.accounts import router
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="test-secret")
app.include_router(router)

@pytest.fixture
def client():
    return TestClient(app)

def test_get_login(client):
    response = client.get("/login")
    response = client.get("/login")
    assert response.status_code == 200
    assert "login" in response.text.lower()

@patch("routers.accounts.check_password", return_value=True)
@patch("routers.accounts.get_user_id", return_value=1)
@patch("routers.accounts.get_user_by_id", return_value=[1, "user", None, None, "role"])
def test_post_login_success(mock_get_user_by_id, mock_get_user_id, mock_check_password, client):
    response = client.post("/login", data={"username": "user", "password": "pass"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/home/1"

@patch("routers.accounts.check_password", return_value=False)
def test_post_login_fail(mock_check_password, client):
    response = client.post("/login", data={"username": "user", "password": "wrong"})
    assert response.status_code == 200
    assert "Invalid username or password" in response.text

def test_get_create_account(client):
    response = client.get("/create_account")
    assert response.status_code == 200
    assert "Create Account" in response.text

@patch("routers.accounts.create_user")
def test_post_create_account(mock_create_user, client):
    response = client.post("/create_account", data={"username": "user", "password": "pass", "avatarUrl": "avatar.png"}, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    mock_create_user.assert_called_once_with("user", "pass", "avatar.png")

def test_logout(client):
    response = client.get("/logout", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"