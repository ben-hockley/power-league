import pytest
from unittest.mock import patch, MagicMock
from services import draft_service

def test_start_new_season_no_link_calls_all_steps():
    league_id = 42
    with patch("services.draft_service.record_new_champion") as mock_champ, \
         patch("services.draft_service.new_season") as mock_season, \
         patch("services.draft_service.age_league_players") as mock_age, \
         patch("services.draft_service.create_draft_class") as mock_draft_class, \
         patch("services.draft_service.wipe_league_records") as mock_wipe, \
         patch("services.draft_service.generate_schedule") as mock_schedule, \
         patch("services.draft_service.schedule_draft") as mock_sched_draft, \
         patch("services.draft_service.order_depth_charts") as mock_order:

        draft_service.start_new_season_no_link(league_id)

        mock_champ.assert_called_once_with(league_id)
        mock_season.assert_called_once_with(league_id)
        mock_age.assert_called_once_with(league_id)
        mock_draft_class.assert_called_once_with(league_id)
        mock_wipe.assert_called_once_with(league_id)
        mock_schedule.assert_called_once_with(league_id)
        mock_sched_draft.assert_called_once_with(league_id)
        mock_order.assert_called_once_with(league_id)

def test_do_auto_draft_picks_flow():
    with patch("services.draft_service.auto_draft_pick") as mock_auto, \
         patch("services.draft_service.get_done_drafts") as mock_get_done, \
         patch("services.draft_service.check_draft_active") as mock_check, \
         patch("services.draft_service.delete_draft") as mock_delete, \
         patch("services.draft_service.start_new_season_no_link") as mock_start:

        # Simulate two drafts, one active, one not
        mock_get_done.return_value = [
            (1, 100, 2025),  # (draft_id, league_id, draft_year)
            (2, 200, 2026)
        ]
        # First draft is active, second is not
        mock_check.side_effect = [True, False]

        draft_service.do_auto_draft_picks()

        mock_auto.assert_called_once()
        assert mock_check.call_count == 2
        mock_delete.assert_called_once_with(200, 2026)
        mock_start.assert_called_once_with(200)