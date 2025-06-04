import pytest
from unittest.mock import patch, MagicMock
import mariadb

# Adjust the import path if needed
from repositories import database

def test_get_db_connection_success(monkeypatch):
    mock_conn = MagicMock()
    def mock_connect(**kwargs):
        return mock_conn
    monkeypatch.setattr(mariadb, "connect", mock_connect)
    conn = database.get_db_connection()
    assert conn == mock_conn

def test_get_db_connection_failure(monkeypatch, capsys):
    def mock_connect(**kwargs):
        raise mariadb.Error("fail")
    monkeypatch.setattr(mariadb, "connect", mock_connect)
    conn = database.get_db_connection()
    assert conn is None
    captured = capsys.readouterr()
    assert "Error connecting to MariaDB" in captured.out

def test_test_db_connection_success(monkeypatch, capsys):
    mock_conn = MagicMock()
    monkeypatch.setattr(database, "get_db_connection", lambda: mock_conn)
    database.test_db_connection()
    captured = capsys.readouterr()
    assert "Connection successful" in captured.out
    mock_conn.close.assert_called_once()

def test_test_db_connection_failure(monkeypatch, capsys):
    monkeypatch.setattr(database, "get_db_connection", lambda: None)
    database.test_db_connection()
    captured = capsys.readouterr()
    assert "Connection failed" in captured.out

def test_test_db_cursor(monkeypatch, capsys):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.fetchall.return_value = [("row1",), ("row2",)]
    monkeypatch.setattr(database, "get_db_connection", lambda: mock_conn)
    database.test_db_cursor(42)
    mock_conn.cursor.assert_called_once()
    mock_cursor.execute.assert_called_once_with("SELECT * FROM players WHERE team_id = 42")
    mock_cursor.fetchall.assert_called_once()
    mock_conn.close.assert_called_once()
    captured = capsys.readouterr()
    assert "row1" in captured.out
    assert "row2" in captured.out