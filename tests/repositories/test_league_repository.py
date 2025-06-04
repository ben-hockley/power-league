import pytest
from unittest.mock import MagicMock
from repositories import league_repository

@pytest.fixture
def mock_conn(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr(league_repository, "get_db_connection", lambda: mock_conn)
    return mock_conn, mock_cursor

def test_get_standings(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("team1",), ("team2",)]
    result = league_repository.get_standings(1)
    cur.execute.assert_called_once()
    conn.close.assert_called_once()
    assert result == [("team1",), ("team2",)]

def test_get_reverse_standings(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("team1",), ("team2",)]
    result = league_repository.get_reverse_standings(1)
    cur.execute.assert_called_once()
    conn.close.assert_called_once()
    assert result == [("team1",), ("team2",)]

def test_get_league_id_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [42]
    result = league_repository.get_league_id(7)
    assert result == 42

def test_get_league_id_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = league_repository.get_league_id(7)
    assert result is None

def test_get_league_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ("league_row",)
    result = league_repository.get_league(1)
    assert result == ("league_row",)

def test_get_league_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = league_repository.get_league(1)
    assert result is None

def test_get_public_leagues(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("league1",), ("league2",)]
    result = league_repository.get_public_leagues()
    assert result == [("league1",), ("league2",)]

def test_get_all_leagues(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("league1",), ("league2",)]
    result = league_repository.get_all_leagues()
    assert result == [("league1",), ("league2",)]

def test_get_league_year_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [2025]
    result = league_repository.get_league_year(1)
    assert result == 2025

def test_get_league_year_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = league_repository.get_league_year(1)
    assert result is None

def test_get_fixtures(mock_conn, monkeypatch):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("fixture1",), ("fixture2",)]
    monkeypatch.setattr(league_repository, "get_league_id", lambda tid: 1)
    result = league_repository.get_fixtures(7)
    assert result == [("fixture1",), ("fixture2",)]

def test_delete_fixture(mock_conn):
    conn, cur = mock_conn
    league_repository.delete_fixture(99)
    cur.execute.assert_called_once()
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_get_today_fixtures(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("fixture1",)]
    result = league_repository.get_today_fixtures()
    assert result == [("fixture1",)]

def test_new_season(mock_conn):
    conn, cur = mock_conn
    league_repository.new_season(1)
    cur.execute.assert_called_once()
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_create_league(mock_conn):
    conn, cur = mock_conn
    league_repository.create_league("Test League", 2025, True, 10, "CODE123")
    cur.execute.assert_called_once()
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_get_owned_leagues(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("league1",)]
    result = league_repository.get_owned_leagues(5)
    assert result == [("league1",)]

def test_get_league_by_code_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ("league_row",)
    result = league_repository.get_league_by_code("CODE123")
    assert result == ("league_row",)

def test_get_league_by_code_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = league_repository.get_league_by_code("CODE123")
    assert result is None

def test_get_league_owner_id_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [77]
    result = league_repository.get_league_owner_id(1)
    assert result == 77

def test_get_league_owner_id_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = league_repository.get_league_owner_id(1)
    assert result is None

def test_save_new_league(mock_conn):
    conn, cur = mock_conn
    league_repository.save_new_league("Test", 2025, True, 99)
    cur.execute.assert_called_once()
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_make_league_active(mock_conn):
    conn, cur = mock_conn
    league_repository.make_league_active(1)
    cur.execute.assert_called_once()
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_get_league_status_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [1]
    result = league_repository.get_league_status(1)
    assert result == 1

def test_get_league_status_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = league_repository.get_league_status(1)
    assert result is None

def test_add_champion_existing_champions(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ["1,2"]
    league_repository.add_champion(1, 3)
    cur.execute.assert_any_call("UPDATE leagues SET champions = ? WHERE id = ?", ("1,2,3", 1))
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_add_champion_no_champions(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [None]
    league_repository.add_champion(1, 3)
    cur.execute.assert_any_call("UPDATE leagues SET champions = ? WHERE id = ?", ("3", 1))
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_get_champions_ids(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ["1,2,3"]
    result = league_repository.get_champions_ids(1)
    assert result == [1, 2, 3]

def test_get_champions_ids_empty(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [None]
    result = league_repository.get_champions_ids(1)
    assert result == []

def test_get_champions_names(mock_conn, monkeypatch):
    conn, cur = mock_conn
    monkeypatch.setattr(league_repository, "get_champions_ids", lambda lid: [1, 2])
    cur.fetchall.return_value = [("Team A",), ("Team B",)]
    result = league_repository.get_champions_names(1)
    assert result == ["Team A", "Team B"]

def test_get_champions_names_empty(monkeypatch):
    monkeypatch.setattr(league_repository, "get_champions_ids", lambda lid: [])
    result = league_repository.get_champions_names(1)
    assert result == []

def test_get_reigning_champion_name_found(mock_conn, monkeypatch):
    conn, cur = mock_conn
    monkeypatch.setattr(league_repository, "get_champions_ids", lambda lid: [1, 2, 3])
    cur.fetchone.return_value = ("Team C",)
    result = league_repository.get_reigning_champion_name(1)
    assert result == ("Team C",)

def test_get_reigning_champion_name_none(monkeypatch):
    monkeypatch.setattr(league_repository, "get_champions_ids", lambda lid: [])
    result = league_repository.get_reigning_champion_name(1)
    assert result is None

def test_get_top_team(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ("team_row",)
    result = league_repository.get_top_team(1)
    assert result == ("team_row",)

def test_record_new_champion(monkeypatch):
    monkeypatch.setattr(league_repository, "get_top_team", lambda lid: [99, "team"])
    called = {}
    def fake_add_champion(lid, cid):
        called["lid"] = lid
        called["cid"] = cid
    monkeypatch.setattr(league_repository, "add_champion", fake_add_champion)
    league_repository.record_new_champion(1)
    assert called["lid"] == 1
    assert called["cid"] == 99

def test_get_number_of_championships(monkeypatch):
    monkeypatch.setattr(league_repository, "get_league_id", lambda tid: 1)
    monkeypatch.setattr(league_repository, "get_champions_ids", lambda lid: [1, 2, 1, 3])
    result = league_repository.get_number_of_championships(1)
    assert result == 2

def test_get_number_of_championships_no_league(monkeypatch):
    monkeypatch.setattr(league_repository, "get_league_id", lambda tid: None)
    result = league_repository.get_number_of_championships(1)
    assert result == 0

def test_get_user_championships_won(mock_conn, monkeypatch):
    conn, cur = mock_conn
    cur.fetchall.return_value = [(1,), (2,)]
    monkeypatch.setattr(league_repository, "get_number_of_championships", lambda tid: 2 if tid == 1 else 1)
    result = league_repository.get_user_championships_won(5)
    assert result == 3

def test_get_last_game_date_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ["2025-06-04"]
    result = league_repository.get_last_game_date(1)
    assert result == "2025-06-04"

def test_get_last_game_date_none(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = league_repository.get_last_game_date(1)
    assert result is None

def test_get_last_seasons_retirements_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ['[{"player_id":1}]']
    result = league_repository.get_last_seasons_retirements(1)
    assert result == [{"player_id": 1}]

def test_get_last_seasons_retirements_none(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [None]
    result = league_repository.get_last_seasons_retirements(1)
    assert result == []