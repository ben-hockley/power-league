import pytest
from unittest.mock import MagicMock
import json
from repositories import game_repository

@pytest.fixture
def mock_conn(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr(game_repository, "get_db_connection", lambda: mock_conn)
    return mock_conn, mock_cursor

def test_save_game(mock_conn):
    conn, cur = mock_conn
    cur.lastrowid = 123
    game_id = game_repository.save_game(1, 2, 3, '{"home_score":10,"away_score":7}')
    cur.execute.assert_called_once()
    conn.commit.assert_called_once()
    conn.close.assert_called_once()
    assert game_id == 123

def test_get_game_by_id_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ("game_row",)
    result = game_repository.get_game_by_id(42)
    cur.execute.assert_called_once_with("SELECT * FROM games WHERE id = ?", (42,))
    conn.close.assert_called_once()
    assert result == ("game_row",)

def test_get_game_by_id_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = game_repository.get_game_by_id(42)
    assert result is None

def test_get_games_by_team_id(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("game1",), ("game2",)]
    result = game_repository.get_games_by_team_id(7)
    cur.execute.assert_called_once_with("SELECT * FROM games WHERE home_team_id = ? OR away_team_id = ?", (7, 7))
    conn.close.assert_called_once()
    assert result == [("game1",), ("game2",)]

def test_get_next_fixture_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ("fixture_row",)
    result = game_repository.get_next_fixture(5)
    cur.execute.assert_called_once()
    conn.close.assert_called_once()
    assert result == ("fixture_row",)

def test_get_next_fixture_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = game_repository.get_next_fixture(5)
    assert result is None