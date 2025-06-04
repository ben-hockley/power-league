import pytest
from unittest.mock import MagicMock, patch
from repositories import user_repository

@pytest.fixture
def mock_conn(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr(user_repository, "get_db_connection", lambda: mock_conn)
    return mock_conn, mock_cursor

def test_get_user_by_username_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ("user1",)
    result = user_repository.get_user_by_username("user1")
    assert result == ("user1",)

def test_get_user_by_username_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = user_repository.get_user_by_username("user1")
    assert result is None

def test_get_user_by_id_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = ("user1",)
    result = user_repository.get_user_by_id(1)
    assert result == ("user1",)

def test_get_user_by_id_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = user_repository.get_user_by_id(1)
    assert result is None

@patch("bcrypt.hashpw", return_value=b"hashedpw")
@patch("bcrypt.gensalt", return_value=b"salt")
def test_create_user(mock_gensalt, mock_hashpw, mock_conn):
    conn, cur = mock_conn
    user_repository.create_user("user1", "password", "avatar.png")
    cur.execute.assert_called_once()
    conn.commit.assert_called_once()
    conn.close.assert_called_once()

@patch("bcrypt.checkpw", return_value=True)
def test_check_password_correct(mock_checkpw, mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [b"hashedpw"]
    result = user_repository.check_password("user1", "password")
    assert result is True

@patch("bcrypt.checkpw", return_value=False)
def test_check_password_incorrect(mock_checkpw, mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [b"hashedpw"]
    result = user_repository.check_password("user1", "wrongpassword")
    assert result is False

def test_check_password_user_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = user_repository.check_password("user1", "password")
    assert result is False

def test_get_user_id_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = [42]
    result = user_repository.get_user_id("user1")
    assert result == 42

def test_get_user_id_not_found(mock_conn):
    conn, cur = mock_conn
    cur.fetchone.return_value = None
    result = user_repository.get_user_id("user1")
    assert result is None