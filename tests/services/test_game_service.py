import pytest
from unittest.mock import patch, MagicMock
from services import game_service

def test_match_report_no_link_calls_all_dependencies():
    home_team_id = 1
    away_team_id = 2
    fake_game_details = {"home_score": 3, "away_score": 2}
    fake_game_details_obj = MagicMock()
    fake_game_id = 99
    fake_game_record = [None, None, None, None, None, '{"home_score": 3, "away_score": 2}']

    with patch("services.game_service.get_match_report", return_value=fake_game_details_obj) as mock_get_match_report, \
         patch("services.game_service.get_team_league_id", return_value=10) as mock_get_team_league_id, \
         patch("services.game_service.game_details_to_json", return_value='{"home_score": 3, "away_score": 2}') as mock_game_details_to_json, \
         patch("services.game_service.save_game", return_value=fake_game_id) as mock_save_game, \
         patch("services.game_service.get_game_by_id", return_value=fake_game_record) as mock_get_game_by_id, \
         patch("services.game_service.json_to_game_details", return_value=fake_game_details) as mock_json_to_game_details, \
         patch("services.game_service.add_result_to_team") as mock_add_result_to_team:

        game_service.match_report_no_link(home_team_id, away_team_id)

        mock_get_match_report.assert_called_once_with(home_team_id, away_team_id)
        mock_get_team_league_id.assert_called_once_with(home_team_id)
        mock_game_details_to_json.assert_called_once_with(fake_game_details_obj)
        mock_save_game.assert_called_once_with(10, home_team_id, away_team_id, '{"home_score": 3, "away_score": 2}')
        mock_get_game_by_id.assert_called_once_with(fake_game_id)
        mock_json_to_game_details.assert_called_once_with('{"home_score": 3, "away_score": 2}')
        # Should be called for both teams
        assert mock_add_result_to_team.call_count == 2
        mock_add_result_to_team.assert_any_call(home_team_id, 3, 2)
        mock_add_result_to_team.assert_any_call(away_team_id, 2, 3)