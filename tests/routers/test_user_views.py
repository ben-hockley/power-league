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

# Mock return values for get_league(league_id)
mock_league_1 = (
    1,                      # ID
    "NFL",                  # name
    3,                      # season_number
    1,                      # is_public
    2024,                   # league_year
    10,                     # admin_id
    1,                      # is_active
    "1,2,3",                # champions
    None,                   # last_seson_retirements
    12,                     # max_teams
    "ABC123"                # code_to_join
)
mock_league_2 = (
    2,                      # ID
    "UFL",                  # name
    4,                      # season_number
    1,                      # is_public
    2025,                   # league_year
    11,                     # admin_id
    0,                      # is_active
    "1,2,3",   # champions
    None,      # last_season_retirements
    16,                     # max_teams
    "XYZ789"                # code_to_join
)
# Mock return values for get_team_by_id(team_id)
mock_team_1 = (
    1,                          # ID
    "Springfield Atoms",        # team_name
    "12,34",                    # depth_qb
    "56,78",                    # depth_rb
    "90,91,92",                 # depth_wr
    "101,102,103,104,105",      # depth_ol
    "110,111,112",              # depth_dl
    "120,121",                  # depth_lb
    "130,131,132,133",          # depth_db
    3,                          # league_id
    7,                          # wins
    2,                          # losses
    210,                        # points_for
    150,                        # points_against
    42,                         # user_id
    "#FF0000",                  # primary_color
    "#00FF00",                  # secondary_color
    "static/badges/Springfield_Atoms_badge.svg"  # badge_path
)
mock_team_2 = (
    2,                          # ID
    "Shelbyville Sharks",       # team_name
    "21,22",                    # depth_qb
    "23,24",                    # depth_rb
    "25,26,27",                 # depth_wr
    "28,29,30,31,32",           # depth_ol
    "33,34,35",                 # depth_dl
    "36,37",                    # depth_lb
    "38,39,40,41",              # depth_db
    4,                          # league_id
    5,                          # wins
    4,                          # losses
    180,                        # points_for
    175,                        # points_against
    43,                         # user_id
    "#0000FF",                  # primary_color
    "#FFFF00",                  # secondary_color
    "static/badges/Shelbyville_Sharks_badge.svg"  # badge_path
)
mock_team_3 = (
    3,                          # ID
    "Capital City Capitals",    # team_name
    "51,52",                    # depth_qb
    "53,54,55",                 # depth_rb
    "56,57,58,59",              # depth_wr
    "60,61,62,63,64",           # depth_ol
    "65,66,67",                 # depth_dl
    "68,69",                    # depth_lb
    "70,71,72,73",              # depth_db
    5,                          # league_id
    8,                          # wins
    1,                          # losses
    240,                        # points_for
    120,                        # points_against
    44,                         # user_id
    "#008000",                  # primary_color
    "#FFD700",                  # secondary_color
    "static/badges/Capital_City_Capitals_badge.svg"  # badge_path
)
# Mock return values for get_player_by_id(player_id)
mock_player_1 = (
    1,              # ID
    "Tom",          # f_name
    "Brady",        # l_name
    28,             # age
    2018,           # draft_year
    12,             # draft_pick
    17,             # skill
    "QB",           # position
    5,              # team_id
    2,              # league_id
    0               # trade_listed
)
mock_player_2 = (
    2,              # ID
    "Jerry",        # f_name
    "Rice",         # l_name
    25,             # age
    2019,           # draft_year
    5,              # draft_pick
    19,             # skill
    "WR",           # position
    1,              # team_id
    3,              # league_id
    0               # trade_listed
)
mock_player_3 = (
    3,              # ID
    "Patrick",      # f_name
    "Mahomes",      # l_name
    27,             # age
    2020,           # draft_year
    1,              # draft_pick
    20,             # skill
    "QB",           # position
    2,              # team_id
    3,              # league_id
    0               # trade_listed
)

@pytest.fixture
def client():
    return TestClient(app)

def test_login_redirect(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == status.HTTP_303_SEE_OTHER
    assert response.headers["location"] == "/login"

def test_get_depth_chart_offense(client, monkeypatch):
    # Return a list or tuple if your template expects it
    monkeypatch.setattr("routers.user_views.get_team_by_id", lambda x: mock_team_1)
    monkeypatch.setattr("routers.user_views.get_depth_chart_by_position", lambda tid, pos: [])
    response = client.get("/depth_chart_offense/1")
    assert response.status_code == 200
    # Optionally, check for a string you know is in your template
    assert "<!DOCTYPE html>" in response.text

def test_get_roster(client, monkeypatch):
    monkeypatch.setattr("routers.user_views.get_team_by_id", lambda x: mock_team_1)
    monkeypatch.setattr("routers.user_views.get_players_by_team", lambda x: [mock_player_1, mock_player_2, mock_player_3])
    response = client.get("/roster/1")
    assert response.status_code == 200

def test_get_league_table(client, monkeypatch):
    monkeypatch.setattr("routers.user_views.get_team_by_id", lambda x: mock_team_1)
    monkeypatch.setattr("routers.user_views.get_league_id", lambda x: 1)
    monkeypatch.setattr("routers.user_views.get_league", lambda x: mock_league_1)
    monkeypatch.setattr("routers.user_views.get_standings", lambda x: [mock_team_1, mock_team_2, mock_team_3])
    response = client.get("/standings/1")
    assert response.status_code == 200

def test_get_league_players(client, monkeypatch):
    monkeypatch.setattr("routers.user_views.get_team_by_id", lambda x: mock_team_1)
    monkeypatch.setattr("routers.user_views.get_league_id", lambda x: 1)
    monkeypatch.setattr("routers.user_views.get_league", lambda x: mock_league_1)
    monkeypatch.setattr("routers.user_views.get_teams_by_league_id", lambda x: [mock_team_1, mock_team_2, mock_team_3])
    monkeypatch.setattr("routers.user_views.get_all_players_by_league", lambda x: [mock_player_1, mock_player_2, mock_player_3])
    response = client.get("/players/1")
    assert response.status_code == 200

# Add more tests for other endpoints as needed, following the above pattern.