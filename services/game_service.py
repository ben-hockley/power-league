from simulator import get_match_report, game_details_to_json, json_to_game_details

from repositories.game_repository import save_game, get_game_by_id
from repositories.team_repository import get_team_league_id, add_result_to_team


def match_report_no_link(home_team_id: int, away_team_id: int):
    GameDetails = get_match_report(home_team_id, away_team_id)

    # save data to the database
    league_id = get_team_league_id(home_team_id)
    details_json = game_details_to_json(GameDetails)

    game_id = save_game(league_id, home_team_id, away_team_id, details_json)

    game_record = get_game_by_id(game_id)
    game_details = game_record[5]
    game_details = json_to_game_details(game_details)

    # get the home score and away score for the game
    homeScore = game_details["home_score"]
    awayScore = game_details["away_score"]

    # add the result to the teams
    add_result_to_team(home_team_id, homeScore, awayScore)
    add_result_to_team(away_team_id, awayScore, homeScore)