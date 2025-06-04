import pytest
from unittest.mock import MagicMock, patch
from repositories import trade_repository

@pytest.fixture
def mock_conn(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr(trade_repository, "get_db_connection", lambda: mock_conn)
    return mock_conn, mock_cursor

def test_save_trade(mock_conn):
    conn, cur = mock_conn
    trade_repository.save_trade(1, 2, "3,4", "5,6")
    cur.execute.assert_called_once()
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_get_trades_proposed(mock_conn, monkeypatch):
    conn, cur = mock_conn
    cur.fetchall.return_value = [
        (10, 1, 2, "3,4", "5,6")
    ]
    monkeypatch.setattr(trade_repository, "get_team_by_id", lambda tid: [tid, f"Team{tid}"])
    monkeypatch.setattr(trade_repository, "get_player_by_id", lambda pid: f"Player{pid}")
    result = trade_repository.get_trades_proposed(1)
    assert result == [{
        "id": 10,
        "proposing_team_id": 1,
        "proposing_team_name": "Team1",
        "receiving_team_id": 2,
        "receiving_team_name": "Team2",
        "players_offered": ["Player3", "Player4"],
        "players_requested": ["Player5", "Player6"],
    }]

def test_get_trades_received(mock_conn, monkeypatch):
    conn, cur = mock_conn
    cur.fetchall.return_value = [
        (11, 2, 1, "7", "8,9")
    ]
    monkeypatch.setattr(trade_repository, "get_team_by_id", lambda tid: [tid, f"Team{tid}"])
    monkeypatch.setattr(trade_repository, "get_player_by_id", lambda pid: f"Player{pid}")
    result = trade_repository.get_trades_received(1)
    assert result == [{
        "id": 11,
        "proposing_team_id": 2,
        "proposing_team_name": "Team2",
        "receiving_team_id": 1,
        "receiving_team_name": "Team1",
        "players_offered": ["Player7"],
        "players_requested": ["Player8", "Player9"],
    }]

def test_delete_trade(mock_conn):
    conn, cur = mock_conn
    trade_repository.delete_trade(99)
    cur.execute.assert_called_once_with("DELETE FROM trades WHERE id = ?", (99,))
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_accept_trade_success(mock_conn, monkeypatch):
    conn, cur = mock_conn
    cur.fetchone.return_value = (12, 1, 2, "3,4", "5")
    monkeypatch.setattr(trade_repository, "cut_player", lambda pid: None)
    monkeypatch.setattr(trade_repository, "sign_player", lambda pid, tid: None)
    monkeypatch.setattr(trade_repository, "delete_trade", lambda tid: None)
    result = trade_repository.accept_trade(12)
    assert result == "Trade accepted successfully."
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_accept_trade_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = trade_repository.accept_trade(999)
    assert result == "Trade not found."
    conn.close.assert_called_once()

def test_trade_list_player(mock_conn):
    conn, cur = mock_conn
    trade_repository.trade_list_player(7)
    cur.execute.assert_called_once_with(
        "UPDATE players SET trade_listed = 1 WHERE id = ?", (7,)
    )
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_untrade_list_player(mock_conn):
    conn, cur = mock_conn
    trade_repository.untrade_list_player(8)
    cur.execute.assert_called_once_with(
        "UPDATE players SET trade_listed = 0 WHERE id = ?", (8,)
    )
    conn.commit.assert_called_once()
    conn.close.assert_called_once()