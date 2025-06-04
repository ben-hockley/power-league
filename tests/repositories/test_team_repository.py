import pytest
from unittest.mock import MagicMock, patch
from repositories import team_repository

@pytest.fixture
def mock_conn(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr(team_repository, "get_db_connection", lambda: mock_conn)
    return mock_conn, mock_cursor

def test_get_teams_by_user_id(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("team1",), ("team2",)]
    result = team_repository.get_teams_by_user_id(1)
    assert result == [("team1",), ("team2",)]

def test_get_team_by_id_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ("team1",)
    result = team_repository.get_team_by_id(1)
    assert result == ("team1",)

def test_get_team_by_id_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = team_repository.get_team_by_id(1)
    assert result is None

def test_get_team_name_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ["The Team"]
    result = team_repository.get_team_name(1)
    assert result == "The Team"

def test_get_team_name_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = team_repository.get_team_name(1)
    assert result is None

def test_get_team_owner_id_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [42]
    result = team_repository.get_team_owner_id(1)
    assert result == 42

def test_get_team_owner_id_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = team_repository.get_team_owner_id(1)
    assert result is None

def test_create_new_team(mock_conn, monkeypatch):
    conn, cur = mock_conn
    cur.lastrowid = 99
    monkeypatch.setattr(team_repository, "fill_new_team", lambda tid: None)
    result = team_repository.create_new_team(1, "Testers", 2, "#fff", "#000", "badge.svg")
    assert result == 99
    assert conn.commit.called
    assert conn.close.called

def test_get_team_league_id_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [5]
    result = team_repository.get_team_league_id(1)
    assert result == 5

def test_get_team_league_id_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = team_repository.get_team_league_id(1)
    assert result is None

@pytest.mark.parametrize("pf,pa,expected", [
    (10, 5, "W"),
    (5, 10, "L"),
    (7, 7, "T"),
])
def test_add_result_to_team(mock_conn, pf, pa, expected):
    conn, cur = mock_conn
    team_repository.add_result_to_team(1, pf, pa)
    assert conn.commit.called
    assert conn.close.called

def test_get_all_teams(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("team1",)]
    result = team_repository.get_all_teams()
    assert result == [("team1",)]

def test_wipe_league_records(mock_conn):
    conn, cur = mock_conn
    team_repository.wipe_league_records(1)
    assert conn.commit.call_count == 3
    assert conn.close.called

@patch("os.path.exists", return_value=True)
@patch("os.remove")
def test_delete_team(mock_remove, mock_exists, mock_conn, monkeypatch):
    conn, cur = mock_conn
    cur.fetchone.side_effect = [["Test Team"], [(1,), (2,)]]
    cur.fetchall.side_effect = [[(1,), (2,)]]
    monkeypatch.setattr(team_repository, "get_team_name", lambda tid: "Test Team")
    team_repository.delete_team(1)
    assert conn.commit.call_count >= 4
    assert conn.close.called
    assert mock_remove.called

def test_get_standings(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("team1",)]
    result = team_repository.get_standings(1)
    assert result == [("team1",)]

def test_order_depth_charts(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.side_effect = (
        [[(1,), (2,)]] +
        [[(1, "QB", 0, 0, 0, 0, 20), (2, "QB", 0, 0, 0, 0, 10)]] * 14
    )
    team_repository.order_depth_charts(1)
    assert conn.commit.called
    assert conn.close.called

def test_order_depth_charts_offense_by_team(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [(1, "QB", 0, 0, 0, 0, 90), (2, "QB", 0, 0, 0, 0, 80)]
    team_repository.order_depth_charts_offense_by_team(1)
    assert conn.commit.called
    assert conn.close.called

def test_order_depth_charts_defense_by_team(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [(1, "DL", 0, 0, 0, 0, 90), (2, "DL", 0, 0, 0, 0, 80)]
    team_repository.order_depth_charts_defense_by_team(1)
    assert conn.commit.called
    assert conn.close.called

def test_get_teams_by_league_id(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("team1",)]
    result = team_repository.get_teams_by_league_id(1)
    assert result == [("team1",)]

def test_get_manager_id_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [7]
    result = team_repository.get_manager_id(1)
    assert result == 7

def test_get_manager_id_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = team_repository.get_manager_id(1)
    assert result is None