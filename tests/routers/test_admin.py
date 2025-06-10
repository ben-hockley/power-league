import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

# Patch require_admin
patcher = patch("dependencies.require_admin", lambda: True)
patcher.start()

from routers.admin import router  # Import AFTER patching

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="test-secret")
app.include_router(router)

@pytest.fixture
def client():
    yield TestClient(app)

@patch("routers.admin.get_all_leagues", return_value=[("league1",)])
@patch("routers.admin.get_all_teams", return_value=[("team1",)])
def test_get_admin(mock_get_teams, mock_get_leagues, client):
    response = client.get("/admin")
    assert response.status_code == 200
    assert "league" in response.text.lower() or "team" in response.text.lower()

@patch("routers.admin.age_league_players")
def test_age_league(mock_age_league_players, client):
    response = client.get("/age_league_players/1", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"
    mock_age_league_players.assert_called_once_with(1)

@patch("routers.admin.create_draft_class")
def test_add_draft_class(mock_create_draft_class, client):
    response = client.get("/create_draft_class/1", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"
    mock_create_draft_class.assert_called_once_with(1)

@patch("routers.admin.generate_schedule")
def test_generate_league_schedule(mock_generate_schedule, client):
    response = client.get("/generate_schedule/1", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"
    mock_generate_schedule.assert_called_once_with(1)
'''
@patch("routers.admin.record_new_champion")
@patch("routers.admin.new_season")
@patch("routers.admin.age_league_players")
@patch("routers.admin.create_draft_class")
@patch("routers.admin.wipe_league_records")
@patch("routers.admin.generate_schedule")
@patch("routers.admin.schedule_draft")
@patch("routers.admin.order_depth_charts")
def test_start_new_season(
    mock_order_depth_charts,
    mock_schedule_draft,
    mock_generate_schedule,
    mock_wipe_league_records,
    mock_create_draft_class,
    mock_age_league_players,
    mock_new_season,
    mock_record_new_champion,
    client
):
    response = client.get("/new_season/1", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"
    mock_record_new_champion.assert_called_once_with(1)
    mock_new_season.assert_called_once_with(1)
    mock_age_league_players.assert_called_once_with(1)
    mock_create_draft_class.assert_called_once_with(1)
    mock_wipe_league_records.assert_called_once_with(1)
    mock_generate_schedule.assert_called_once_with(1)
    mock_schedule_draft.assert_called_once_with(1)
    mock_order_depth_charts.assert_called_once_with(1)
'''
@patch("routers.admin.wipe_league_records")
def test_wipe_the_league_records(mock_wipe_league_records, client):
    response = client.get("/wipe_league_records/1", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"
    mock_wipe_league_records.assert_called_once_with(1)

@patch("routers.admin.get_match_report", return_value={"home_score": 1, "away_score": 2})
@patch("routers.admin.get_team_league_id", return_value=1)
@patch("routers.admin.game_details_to_json", return_value="{}")
@patch("routers.admin.save_game", return_value=1)
@patch("routers.admin.get_game_by_id", return_value=[None, None, None, None, None, None])
@patch("routers.admin.json_to_game_details", return_value={"home_score": 1, "away_score": 2})
@patch("routers.admin.add_result_to_team")
def test_match_report(
    mock_add_result_to_team,
    mock_json_to_game_details,
    mock_get_game_by_id,
    mock_save_game,
    mock_game_details_to_json,
    mock_get_team_league_id,
    mock_get_match_report,
    client
):
    response = client.get("/match_report/1/2", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"
    mock_get_match_report.assert_called_once_with(1, 2)
    mock_get_team_league_id.assert_called_once_with(1)
    mock_game_details_to_json.assert_called()
    mock_save_game.assert_called()
    mock_get_game_by_id.assert_called()
    mock_json_to_game_details.assert_called()
    assert mock_add_result_to_team.call_count == 2

@patch("routers.admin.create_league")
def test_create_new_league(mock_create_league, client):
    data = {
        "league_name": "Test League",
        "league_year": "2025",
        "is_public": "on",
        "max_teams": "10",
        "league_code": ""
    }
    response = client.post("/create_league", data=data, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"
    mock_create_league.assert_called()

@patch("routers.admin.generate_schedule")
@patch("routers.admin.schedule_draft")
@patch("routers.admin.create_draft_class")
@patch("routers.admin.order_depth_charts")
@patch("routers.admin.make_league_active")
def test_start_new_league(
    mock_make_league_active,
    mock_order_depth_charts,
    mock_create_draft_class,
    mock_schedule_draft,
    mock_generate_schedule,
    client
):
    data = {
        "league_id": "1"
    }
    response = client.post("/start_new_league", data=data, follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin"
    mock_generate_schedule.assert_called_once_with("1")
    mock_schedule_draft.assert_called_once_with("1")
    mock_create_draft_class.assert_called_once_with("1")
    mock_order_depth_charts.assert_called_once_with("1")
    mock_make_league_active.assert_called_once_with("1")

import atexit
atexit.register(patcher.stop)