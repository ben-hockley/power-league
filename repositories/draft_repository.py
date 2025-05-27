from repositories.database import get_db_connection
from datetime import datetime, timedelta
from repositories.league_repository import get_reverse_standings
from repositories.player_repository import add_player_to_depth_chart

def check_draft_active(league_id: int, draft_year: int) -> bool:
    """
    Check if a draft is active for a given league and draft year.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT is_active FROM drafts WHERE league_id = ? AND year = ?",
        (league_id, draft_year)
    )
    is_active = cur.fetchone()
    conn.close()
    if is_active:
        is_active = is_active[0]
    else:
        return False
    return is_active
# when the draft is started, add it to the drafts table
def add_draft(league_id: int, draft_year: int):
    """
    Add a draft to the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    # set the current pick to 1 and the pick deadline to 5 minutes from now
    cur.execute(
        "INSERT INTO drafts (league_id, year, current_pick, pick_deadline, is_active) VALUES (?, ?, ?, ?, ?)",
        (league_id, draft_year, 1, datetime.now() + timedelta(minutes=5), True)
    )
    conn.commit()
    conn.close()

def get_draft_id(league_id: int, draft_year: int):
    """
    Get the draft id for a given league and draft year.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM drafts WHERE league_id = ? AND year = ?",
        (league_id, draft_year)
    )
    draft_id = cur.fetchone()[0]
    conn.close()
    return draft_id

def make_draft_pick(league_id: int, draft_year: int, player_id: int):
    """
    Make a draft pick for a given league and draft year.
    """

    # get the draft order for the league (returns a list of teams)
    draft_order = get_reverse_standings(league_id)
    # repeat the draft order 5 times (5 round draft)
    draft_order = draft_order * 5
    conn = get_db_connection()
    cur = conn.cursor()

    # get the current pick of the draft
    cur.execute("SELECT current_pick FROM drafts WHERE league_id = ? AND year = ?",
        (league_id, draft_year)
    )
    current_pick = cur.fetchone()[0]

    # get the team id for the current pick
    pick_index = current_pick - 1

    if pick_index >= len(draft_order):
        # set the draft to inactive if the current pick exceeds the draft order
        cur.execute(
            "UPDATE drafts SET is_active = ? WHERE league_id = ? AND year = ?",
            (0, league_id, draft_year))
        conn.commit()
        conn.close()
    else:
        team_id = draft_order[pick_index][0]

        cur.execute(
        "UPDATE players SET draft_pick = ?, team_id = ? WHERE id = ?",
        (current_pick, team_id, player_id)
        )
        conn.commit()
        # increment the current pick, set the pick deadline to 5 minutes after the pick was made.
        cur.execute(
            "UPDATE drafts SET current_pick = current_pick + 1, pick_deadline = ? WHERE league_id = ? AND year = ?",
            (datetime.now() + timedelta(minutes=5), league_id, draft_year)
        )
        conn.commit()

        # add the player to the depth chart of the team
        add_player_to_depth_chart(team_id, player_id)

        # if it is the last pick of the draft, set the draft to inactive
        if current_pick >= len(draft_order):
            cur.execute(
                "UPDATE drafts SET is_active = ? WHERE league_id = ? AND year = ?",
                (0, league_id, draft_year)
            )
            conn.commit()
        conn.close()

    

def get_remaining_players(league_id: int, draft_year: int):
    """
    Get the remaining players for a given league and draft year.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM players WHERE league_id = ? AND draft_year = ? AND draft_pick IS NULL",
        (league_id, draft_year)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

'''
def set_draft_order(draft_id: int):
    """
    Set the draft order for a given draft.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    # get the league_id for the draft
    cur.execute("SELECT league_id FROM drafts WHERE id = ?",
        (draft_id,)
    )
    league_id = cur.fetchone()[0]
    # get the league standings (reverse order)
    cur.execute("SELECT * FROM teams WHERE league_id = ? ORDER BY wins ASC, points_for ASC, points_against DESC",
        (league_id,)
    )
    teams = cur.fetchall()
    # set the draft order as a list of team ids
    draft_order = []
    for i in range(5):
        for team in teams:
            draft_order.append(team[0])
    # set the draft order in the database
    for i, team_id in enumerate(draft_order):
        cur.execute(
            "INSERT INTO draft_orders (draft_id, pick_no, team_id) VALUES (?, ?, ?)",
            (draft_id, i + 1, team_id)
        )
    conn.commit()
    conn.close()
'''
def get_picking_team_id(league_id: int, draft_year: int):
    """
    Get the team id for the current pick.
    """
    # get the draft order for the league (returns a list of teams)
    draft_order = get_reverse_standings(league_id)
    # repeat the draft order 5 times (5 round draft)
    draft_order = draft_order * 5

    conn = get_db_connection()
    cur = conn.cursor()
    # get the current pick of the draft
    cur.execute("SELECT current_pick FROM drafts WHERE league_id = ? AND year = ?",
        (league_id, draft_year)
    )
    current_pick = cur.fetchone()[0]
    # get the team id for the current pick
    pick_index = current_pick - 1
    if pick_index >= len(draft_order):
        picking_team = None
    else:
        picking_team = draft_order[pick_index][0]
    return picking_team

def get_last_pick(draft_year: int, league_id: int):
    """
    Get the last pick for a given draft.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # get the draft id for the given league and draft year
    cur.execute(
        "SELECT id FROM drafts WHERE league_id = ? AND year = ?",
        (league_id, draft_year)
    )
    draft_id = cur.fetchone()[0]

    cur.execute(
        "SELECT current_pick FROM drafts WHERE id = ?",
        (draft_id,)
    )
    current_pick = cur.fetchone()[0]
    last_pick = current_pick - 1
    
    # get the last player drafted
    cur.execute(
        "SELECT * FROM players WHERE league_id = ? AND draft_year = ? AND draft_pick = ?",
        (league_id, draft_year, last_pick)
    )
    player = cur.fetchone()
    conn.close()
    return player

def get_players_drafted(league_id: int, draft_year: int):
    """
    Get the players drafted for a given league and draft year.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM players WHERE league_id = ? AND draft_year = ? AND draft_pick IS NOT NULL ORDER BY draft_pick ASC",
        (league_id, draft_year)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def get_time_on_clock(league_id: int, draft_year: int):
    """
    Get the time left on the clock for a given league and draft year.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT pick_deadline FROM drafts WHERE league_id = ? AND year = ?",
        (league_id, draft_year)
    )
    pick_deadline = cur.fetchone()[0]
    time_left = pick_deadline - datetime.now()
    conn.close()
    return time_left

def schedule_draft(league_id: int):
    """
    Save the draft as a fixture in the fixtures table, with home_team_id and away_team_id set to 0.
    The date should be in the format 'YYYY-MM-DD'. 
    Execute this after generating the schedule for the league, set the draft date to the day after
    the last game of the season.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # get the last game date for the league
    cur.execute("SELECT date FROM fixtures WHERE league_id = ? ORDER BY date DESC LIMIT 1", (league_id,))
    date = cur.fetchone()[0]

    # add one day to the date (schedule the draft for the day after the last game)
    date = datetime.strptime(str(date), '%Y-%m-%d') + timedelta(days=1)
    date = date.strftime('%Y-%m-%d')

    cur.execute(
        "INSERT INTO fixtures (league_id, date, home_team_id, away_team_id) VALUES (?, ?, ?, ?)",
        (league_id, date, 0, 0)
    )
    conn.commit()
    conn.close()

def get_draft_date(league_id: int):
    """
    Get the draft date for a given league.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT date FROM fixtures WHERE league_id = ? AND home_team_id = 0 AND away_team_id = 0",
        (league_id,)
    )
    date = cur.fetchone()
    conn.close()
    if date:
        return date[0]
    return None

def draft_best_available_player(league_id: int, draft_year: int):
    """
    Draft the best available player for a given league and draft year.
    Use this when the draft clock expires and the team has not made a pick.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # get the remaining players
    cur.execute(
        "SELECT * FROM players WHERE league_id = ? AND draft_year = ? AND draft_pick IS NULL ORDER BY skill DESC LIMIT 1",
        (league_id, draft_year)
    )
    player = cur.fetchone()
    conn.close()
    if player:
        make_draft_pick(league_id, draft_year, player[0])  # player[0] is the player_id

def auto_draft_pick():
    """
    Automatically draft a player for the current team if the draft clock expires.
    """
    now = datetime.now()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM drafts WHERE is_active = 1 and pick_deadline < ?", (now,))
    expired_picks = cur.fetchall()
    conn.close()
    if expired_picks:
        for draft in expired_picks:
            draft_best_available_player(draft[1], draft[2])  # draft[1] is league_id, draft[2] is draft_year
    #print(f"Auto drafter ran successfully at {now}.")
