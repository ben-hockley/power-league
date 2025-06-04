import pytest
from unittest.mock import MagicMock, patch
from repositories import player_repository

@pytest.fixture
def mock_conn(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr(player_repository, "get_db_connection", lambda: mock_conn)
    return mock_conn, mock_cursor

def test_add_player_to_depth_chart(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.side_effect = [("QB",), ("1,2",)]
    player_repository.add_player_to_depth_chart(1, 3)
    assert cur.execute.call_count >= 3
    assert conn.commit.called
    assert conn.close.called

def test_get_players(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("player1",), ("player2",)]
    result = player_repository.get_players(1)
    assert result == [("player1",), ("player2",)]

def test_get_player_by_id(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ("player1",)
    result = player_repository.get_player_by_id(5)
    assert result == ("player1",)

def test_get_depth_chart(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.side_effect = [("player1",), ("player2",)]
    result = player_repository.get_depth_chart("1,2")
    assert result == ["player1", "player2"]

def test_get_depth_chart_string_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ["1,2,3"]
    result = player_repository.get_depth_chart_string(1, "QB")
    assert result == "1,2,3"

def test_get_depth_chart_string_none(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = player_repository.get_depth_chart_string(1, "QB")
    assert result is None

def test_get_depth_chart_by_position_found(monkeypatch):
    monkeypatch.setattr(player_repository, "get_depth_chart_string", lambda tid, pos: "1,2")
    monkeypatch.setattr(player_repository, "get_depth_chart", lambda s: ["player1", "player2"])
    result = player_repository.get_depth_chart_by_position(1, "QB")
    assert result == ["player1", "player2"]

def test_get_depth_chart_by_position_none(monkeypatch):
    monkeypatch.setattr(player_repository, "get_depth_chart_string", lambda tid, pos: None)
    result = player_repository.get_depth_chart_by_position(1, "QB")
    assert result is None

def test_save_depth_chart(mock_conn):
    conn, cur = mock_conn
    player_repository.save_depth_chart(1, "QB", "1,2,3")
    cur.execute.assert_called_once()
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

def test_clean_depth_chart_string(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [",1,2,3,"]
    player_repository.clean_depth_chart_string("QB", 1)
    cur.execute.assert_any_call("UPDATE teams SET depth_qb = ? WHERE id = ?", ("1,2,3", 1))
    conn.commit.assert_called()
    conn.close.assert_called_once()

def test_clean_all_depth_charts(monkeypatch):
    called = []
    monkeypatch.setattr(player_repository, "clean_depth_chart_string", lambda pos, tid: called.append((pos, tid)))
    player_repository.clean_all_depth_charts(1)
    assert len(called) == 7

def test_sort_depth_chart(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ["3,1,2"]
    player_repository.sort_depth_chart(1, "QB")
    cur.execute.assert_any_call("UPDATE teams SET depth_qb = ? WHERE id = ?", ("1,2,3", 1))
    conn.commit.assert_called()
    conn.close.assert_called_once()

def test_sort_all_depth_charts(monkeypatch):
    called = []
    monkeypatch.setattr(player_repository, "sort_depth_chart", lambda tid, pos: called.append((tid, pos)))
    player_repository.sort_all_depth_charts(1)
    assert len(called) == 7

def test_get_players_by_team(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("player1",)]
    result = player_repository.get_players_by_team(1)
    assert result == [("player1",)]

def test_get_all_player_ids(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [(1,), (2,)]
    result = player_repository.get_all_player_ids()
    assert result == [1, 2]

def test_get_free_agents(mock_conn, monkeypatch):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("player1",)]
    monkeypatch.setattr(player_repository, "get_league_year", lambda lid: 2025)
    result = player_repository.get_free_agents(1)
    assert result == [("player1",)]

def test_cut_player(mock_conn, monkeypatch):
    conn, cur = mock_conn
    monkeypatch.setattr(player_repository, "get_player_by_id", lambda pid: [1, "fn", "ln", 25, None, None, None, "QB", 1])
    monkeypatch.setattr(player_repository, "get_depth_chart_string", lambda tid, pos: "1,2,3")
    monkeypatch.setattr(player_repository, "save_depth_chart", lambda tid, pos, s: None)
    player_repository.cut_player(1)
    assert conn.commit.called
    assert conn.close.called

def test_sign_player(mock_conn, monkeypatch):
    conn, cur = mock_conn
    monkeypatch.setattr(player_repository, "add_player_to_depth_chart", lambda tid, pid: None)
    player_repository.sign_player(1, 2)
    cur.execute.assert_called_once_with("UPDATE players SET team_id = ? WHERE id = ?", (2, 1))
    conn.commit.assert_called()
    conn.close.assert_called_once()

def test_delete_player(mock_conn, monkeypatch):
    conn, cur = mock_conn
    with patch("os.remove") as mock_remove:
        player_repository.delete_player(1)
        cur.execute.assert_called_once_with("DELETE FROM players WHERE id = ?", (1,))
        conn.commit.assert_called_once()
        conn.close.assert_called_once()
        mock_remove.assert_called_once()

def test_get_star_players(mock_conn):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("player1",), ("player2",)]
    result = player_repository.get_star_players(1)
    assert result == [("player1",), ("player2",)]

def test_get_all_players_by_league(mock_conn, monkeypatch):
    conn, cur = mock_conn
    cur.fetchall.return_value = [("player1",)]
    monkeypatch.setattr(player_repository, "get_league_year", lambda lid: 2025)
    result = player_repository.get_all_players_by_league(1)
    assert result == [("player1",)]