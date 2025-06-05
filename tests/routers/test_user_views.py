import pytest
from fastapi.testclient import TestClient
from fastapi import status, FastAPI
from starlette.middleware.sessions import SessionMiddleware
from routers.user_views import router
import routers.user_views

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="testsecret")
app.include_router(router)

# Dependency override for require_team_owner
def always_allow():
    return True

app.dependency_overrides[routers.user_views.require_team_owner] = always_allow


@pytest.fixture
def client():
    return TestClient(app)

def test_login_redirect(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == "/login"

def test_get_depth_chart_offense(client, monkeypatch):
    # Return a list or tuple if your template expects it
    monkeypatch.setattr("routers.user_views.get_team_by_id", lambda x: [None, None, None, None])
    monkeypatch.setattr("routers.user_views.get_depth_chart_by_position", lambda tid, pos: [])
    response = client.get("/depth_chart_offense/1")
    assert response.status_code == 200
    # Optionally, check for a string you know is in your template
    assert "<!DOCTYPE html>" in response.text

def test_get_roster(client, monkeypatch):
    monkeypatch.setattr("routers.user_views.get_team_by_id", lambda x: [None, None, None, "Test Team"])
    monkeypatch.setattr("routers.user_views.get_players_by_team", lambda x: [[None, None, None, "Player", 1]])
    response = client.get("/roster/1")
    assert response.status_code == 200

def test_get_league_table(client, monkeypatch):
    monkeypatch.setattr("routers.user_views.get_team_by_id", lambda x: [None, None, None, "Test Team"])
    monkeypatch.setattr("routers.user_views.get_league_id", lambda x: 1)
    monkeypatch.setattr("routers.user_views.get_league", lambda x: [None, None, None, "Test League"])
    monkeypatch.setattr("routers.user_views.get_standings", lambda x: [])
    response = client.get("/standings/1")
    assert response.status_code == 200

def test_get_league_players(client, monkeypatch):
    monkeypatch.setattr("routers.user_views.get_team_by_id", lambda x: [1, "Test Team"])
    monkeypatch.setattr("routers.user_views.get_league_id", lambda x: 1)
    monkeypatch.setattr("routers.user_views.get_league", lambda x: [1, "Test League"])
    monkeypatch.setattr("routers.user_views.get_teams_by_league_id", lambda x: [[1, "Test Team"], [2, "Other Team"]])
    # Ensure player[8] is an int, not None
    monkeypatch.setattr("routers.user_views.get_all_players_by_league", lambda x: [[1, "Player", None, None, None, None, None, None, 2]])
    response = client.get("/players/1")
    assert response.status_code == 200

# Add more tests for other endpoints as needed, following the above pattern.