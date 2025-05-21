from unittest.mock import patch
from repositories.user_repository import check_password

@patch("repositories.user_repository.get_user_by_username")
def test_check_password(mock_get_user):
    mock_get_user.return_value = {"username": "test", "password": "hashed"}
    assert not check_password("test", "wrongpassword")