import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta

from repositories import draft_repository

@pytest.fixture
def mock_conn(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr(draft_repository, "get_db_connection", lambda: mock_conn)
    return mock_conn, mock_cursor

def test_check_draft_active_true(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = (1,)
    result = draft_repository.check_draft_active(1, 2024)
    assert result == True  # Use == instead of is

def test_check_draft_active_false(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = draft_repository.check_draft_active(1, 2024)
    assert result is False

def test_add_draft(mock_conn):
    conn, cur = mock_conn
    with patch("repositories.draft_repository.TIME_BETWEEN_PICKS", {"minutes": 5, "seconds": 0}):
        draft_repository.add_draft(1, 2024)
    assert cur.execute.called
    assert conn.commit.called
    assert conn.close.called

def test_get_draft_id(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [42]
    result = draft_repository.get_draft_id(1, 2024)
    assert result == 42

def test_get_remaining_players(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("player1",), ("player2",)]
    result = draft_repository.get_remaining_players(1, 2024)
    assert result == [("player1",), ("player2",)]

def test_get_players_drafted(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("player1",), ("player2",)]
    result = draft_repository.get_players_drafted(1, 2024)
    assert result == [("player1",), ("player2",)]

def test_get_time_on_clock(mock_conn):
    conn, cur = mock_conn
    future = datetime.now() + timedelta(minutes=5)
    cur.fetchone.return_value = [future]
    result = draft_repository.get_time_on_clock(1, 2024)
    assert isinstance(result, timedelta)
    assert result.total_seconds() > 0

def test_get_draft_date(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ["2025-06-04"]
    result = draft_repository.get_draft_date(1)
    assert result == "2025-06-04"

def test_get_draft_date_none(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = draft_repository.get_draft_date(1)
    assert result is None

def test_delete_draft(mock_conn):
    conn, cur = mock_conn
    draft_repository.delete_draft(1, 2024)
    cur.execute.assert_called_once()
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_get_done_drafts(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("draft1",), ("draft2",)]
    result = draft_repository.get_done_drafts()
    assert result == [("draft1",), ("draft2",)]