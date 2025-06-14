from repositories.league_repository import record_new_champion, new_season, generate_schedule
from repositories.player_repository import age_league_players, create_draft_class, reset_season_stats
from repositories.team_repository import wipe_league_records, order_depth_charts, get_teams_by_league_id, recover_depth_chart
from repositories.draft_repository import get_done_drafts, auto_draft_pick, check_draft_active, \
delete_draft, schedule_draft

def start_new_season_no_link(league_id: int):
    # this is the process of initializing a new league season
    # 1 . record the new champion of the league
    record_new_champion(league_id)
    # 1. increase the league year and season number by 1
    new_season(league_id)
    # 2. age the players (includes retirements and skill changes)
    age_league_players(league_id)
    # 3. create a draft class
    create_draft_class(league_id)
    # 4.wipe the league records
    wipe_league_records(league_id)
    # 5. reset the season stats for all players
    reset_season_stats(league_id)
    # 6. generate a new schedule
    generate_schedule(league_id)
    # 7. schedule the draft by saving it as a fixture where home and away team ids are 0.
    schedule_draft(league_id)
    # 8. order the depth charts in order of skill
    order_depth_charts(league_id)
    # 9. check the team depth charts for faulty depth charts and correct if necessary.
    check_team_depth_charts(league_id)

def do_auto_draft_picks():
    auto_draft_pick()

    # get each draft that has no finished
    done_drafts = get_done_drafts()

    for draft in done_drafts:
        league_id = draft[1]
        draft_year = draft[2]
        if check_draft_active(league_id, draft_year) == False:
            delete_draft(league_id, draft_year) # delete the draft from the database.
            start_new_season_no_link(league_id) # start a new season for the league.

def check_team_depth_charts(league_id: int):
    # checks all the teams in the league for faulty depth charts and corrects if necessary.
    teams = get_teams_by_league_id(league_id)
    positions = ["QB", "RB", "WR", "OL", "DL", "LB", "DB"]
    for team in teams:
        for i in range(2, 9):
            if team[i] is None or team[i] == "":
                recover_depth_chart(team[0], positions[i - 2])
