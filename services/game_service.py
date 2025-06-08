from simulator import get_match_report, game_details_to_json, json_to_game_details

from repositories.game_repository import save_game, get_game_by_id
from repositories.team_repository import get_team_league_id, add_result_to_team
from repositories.player_repository import add_passing_stats, add_rushing_stats, add_receiving_stats


def match_report_no_link(home_team_id: int, away_team_id: int):
    GameDetails: dict = get_match_report(home_team_id, away_team_id)

    passing_stats: dict = GameDetails.get("passing_stats")
    rushing_stats: dict = GameDetails.get("rushing_stats")
    receiving_stats: dict = GameDetails.get("receiving_stats")

    # get the box score stats for each player, and add them to their player stats profile.
    if passing_stats:
        for player in passing_stats.keys():
            player_id = player.id
            player_stats = passing_stats[player]
            attempts = player_stats.attempts
            completions = player_stats.completions
            yards = player_stats.yards
            td = player_stats.td

            add_passing_stats(player_id, attempts, completions, yards, td)
        
    if rushing_stats:
        for player in rushing_stats.keys():
            player_id = player.id
            player_stats = rushing_stats[player]
            attempts = player_stats.attempts
            yards = player_stats.yards
            td = player_stats.td

            add_rushing_stats(player_id, attempts, yards, td)
    
    if receiving_stats:
        for player in receiving_stats.keys():
            player_id = player.id
            player_stats = receiving_stats[player]
            receptions = player_stats.receptions
            yards = player_stats.yards
            td = player_stats.td

            add_receiving_stats(player_id, receptions, yards, td)


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