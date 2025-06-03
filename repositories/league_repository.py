from repositories.database import get_db_connection
from datetime import date, timedelta
import json

def get_standings(leagueId: int):
    """
    Get the standings from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM teams WHERE league_id = ? ORDER BY wins DESC, points_for DESC, points_against", (leagueId,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_reverse_standings(leagueId: int):
    """
    Get the reverse standings from the database.
    """
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
    cur.execute("SELECT * FROM teams WHERE league_id = ? ORDER BY wins ASC, points_for ASC, points_against DESC", (leagueId,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_league_id(teamId: int):
    """
    Get the league ID for a specific team from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT league_id FROM teams WHERE id = ?", (teamId,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None
    
def get_league(leagueId: int):
    """
    Get the league name for a specific league ID from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM leagues WHERE id = ?", (leagueId,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row
    else:
        return None
    
def get_public_leagues():
    """
    Get all public leagues from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM leagues WHERE is_public = 1")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_leagues():
    """
    Get all leagues from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM leagues")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_league_year(leagueId: int):
    """
    Get the league year for a specific league ID from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT league_year FROM leagues WHERE id = ?", (leagueId,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None


class Fixture:
    def __init__(self, league_id: int, home_team_id: int, away_team_id: int, played_on: date):
        self.league_id = league_id
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.played_on = played_on

def generate_schedule(leagueId: int):
    """
    Generate a double round-robin schedule for a specific league ID.
    Each team plays every other team twice (home and away), one game per team per day.
    The first day of the schedule is the day after date_initialized.
    Returns a list of Fixture objects.
    """

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM teams WHERE league_id = ?", (leagueId,))
    teams = [row[0] for row in cur.fetchall()]
    conn.close()

    num_teams = len(teams)
    if num_teams < 2:
        return []

    date_initialized = date.today()
    fixtures = []

    # Generate all home/away pairs (double round robin)
    matches = []
    for i in range(num_teams):
        for j in range(num_teams):
            if i != j:
                matches.append((teams[i], teams[j]))

    # To ensure each team plays once per day, use a round-robin scheduler
    # We'll use the circle method for round robin tournaments
    rounds = []
    team_list = teams.copy()
    if num_teams % 2 != 0:
        team_list.append(None)  # Add a dummy team for byes

    n = len(team_list)
    num_rounds = n - 1
    half = n // 2

    # First leg (home/away)
    for round_num in range(num_rounds):
        round_matches = []
        for i in range(half):
            t1 = team_list[i]
            t2 = team_list[n - 1 - i]
            if t1 is not None and t2 is not None:
                round_matches.append((t1, t2))
        # Rotate teams
        team_list = [team_list[0]] + [team_list[-1]] + team_list[1:-1]
        rounds.append(round_matches)

    # Second leg (reverse home/away)
    # Rebuild team_list for the second leg
    team_list = teams.copy()
    if num_teams % 2 != 0:
        team_list.append(None)
    n = len(team_list)
    for round_num in range(num_rounds):
        round_matches = []
        for i in range(half):
            t1 = team_list[i]
            t2 = team_list[n - 1 - i]
            if t1 is not None and t2 is not None:
                round_matches.append((t2, t1))  # Reverse home/away
        # Rotate teams
        team_list = [team_list[0]] + [team_list[-1]] + team_list[1:-1]
        rounds.append(round_matches)

    # Flatten rounds and assign dates
    current_date = date_initialized + timedelta(days=1)
    for round_matches in rounds:
        for home_id, away_id in round_matches:
            fixtures.append(Fixture(leagueId, home_id, away_id, current_date))
        current_date += timedelta(days=1)

    conn = get_db_connection()
    cur = conn.cursor()

    for fixture in fixtures:
        league_id = fixture.league_id
        home_id = fixture.home_team_id
        away_id = fixture.away_team_id
        current_date = fixture.played_on
        # Insert into the database
        cur.execute("INSERT INTO fixtures (league_id, home_team_id, away_team_id, date) VALUES (?, ?, ?, ?)",
                    (league_id, home_id, away_id, current_date))
        conn.commit()
    conn.close()

def get_fixtures(teamId: int):
    """
    Get all fixtures for a specific team from the database.
    """
    leagueId = get_league_id(teamId)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM fixtures WHERE league_id = ? AND (home_team_id = ? OR away_team_id = ?)", (leagueId, teamId, teamId))
    rows = cur.fetchall()
    conn.close()
    return rows

# after simulating a game, delete the fixture.
def delete_fixture(fixtureId: int):
    """
    Delete a fixture from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM fixtures WHERE id = ?", (fixtureId,))
    conn.commit()
    conn.close()

def get_today_fixtures():
    """
    Get all fixtures for today from the database.
    """
    today = date.today()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM fixtures WHERE date = ?", (today,))
    rows = cur.fetchall()
    conn.close()
    return rows

def new_season(leagueId: int):
    """
    Start a new season for a specific league ID.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE leagues SET league_year = league_year + 1, season_number = season_number + 1  WHERE id = ?", (leagueId,))
    conn.commit()
    conn.close()

def create_league(league_name: str, league_year: int, is_public: bool, max_teams: int, code_to_join: str = None):
    """
    Create a new league in the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO leagues (name, season_number, league_year, is_public, is_active, max_teams, code_to_join) VALUES (?, ?, ?, ?, ?, ?, ?)", (league_name, 1, league_year, is_public, 0, max_teams, code_to_join))
    conn.commit()
    conn.close()

def get_owned_leagues(user_id: int):
    """
    Get all leagues owned by a specific user from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM leagues WHERE admin_id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_league_by_code(code: str):
    """
    Get a league by its join code from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM leagues WHERE code_to_join = ?", (code,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row
    else:
        return None

def get_league_owner_id(league_id: int):
    """
    Get the owner ID for a specific league from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT admin_id FROM leagues WHERE id = ?", (league_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None
    
def save_new_league(league_name: str, league_year: int, is_public: bool, admin_id: int):
    """
    Save a new league to the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO leagues (name, season_number, league_year, is_public, admin_id, is_active) VALUES (?, ?, ?, ?, ?, ?)", (league_name, 1, league_year, is_public, admin_id, 0))
    conn.commit()
    conn.close()

def make_league_active(league_id: int):
    """
    Make a league active in the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE leagues SET is_active = 1 WHERE id = ?", (league_id,))
    conn.commit()
    conn.close()

def get_league_status(league_id: int):
    """
    Get the status of a league from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT is_active FROM leagues WHERE id = ?", (league_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None
    
def add_champion(league_id: int, team_id: int):
    """
    Add a champion to the league.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT champions FROM leagues WHERE id = ?", (league_id,))
    row = cur.fetchone()
    if row:
        champions = row[0]
        if champions:
            champions = f"{champions},{team_id}"
        else:
            champions = str(team_id)
        cur.execute("UPDATE leagues SET champions = ? WHERE id = ?", (champions, league_id))
    else:
        champions = str(team_id)
        cur.execute("UPDATE leagues SET champions = ? WHERE id = ?", (champions, league_id))
    conn.commit()
    conn.close()

def get_champions_ids(league_id: int):
    """
    Get the champions of a league, returns a list of team IDs.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT champions FROM leagues WHERE id = ?", (league_id,))
    row = cur.fetchone()
    conn.close()
    if row and row[0]:
        return [int(champion) for champion in row[0].split(',')]
    else:
        return []

def get_champions_names(league_id: int):
    """
    Get the champions of a league, returns a list of team names.
    """
    champions_ids = get_champions_ids(league_id)
    if not champions_ids:
        return []

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT team_name FROM teams WHERE id IN ({})".format(','.join('?' * len(champions_ids))), champions_ids)
    rows = cur.fetchall()
    conn.close()
    
    return [row[0] for row in rows]

def get_reigning_champion_name(league_id: int):
    """
    Get the reigning champion of a league.
    Returns the team name of the reigning champion.
    """
    champions_ids = get_champions_ids(league_id)
    if not champions_ids:
        return None

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT team_name FROM teams WHERE id = ?", (champions_ids[-1],))
    row = cur.fetchone()
    conn.close()
    
    if row:
        return row
    else:
        return None

def get_top_team(leagueId: int):
    """
    Get the top team in the standings for a league.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM teams WHERE league_id = ? ORDER BY wins DESC, points_for DESC, points_against ASC LIMIT 1",
        (leagueId,)
    )
    row = cur.fetchone()
    conn.close()
    return row

def record_new_champion(leagueId: int):
    """
    Record a new champion for a league.
    """
    champion = get_top_team(leagueId)
    champion_id = champion[0]
    add_champion(leagueId, champion_id)

def get_number_of_championships(teamId: int):
    """
    Get the number of championships won by a team in a league.
    """
    league_id = get_league_id(teamId)
    if not league_id:
        return 0
    champions_ids = get_champions_ids(league_id)
    return champions_ids.count(teamId)

def get_user_championships_won(user_id: int):
    """
    Get the number of championships won by a user across all leagues.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM teams WHERE user_id = ?", (user_id,))
    teams = cur.fetchall()
    total_championships = 0
    for team in teams:
        team_id = team[0]
        championships_won = get_number_of_championships(team_id)
        total_championships += championships_won
    conn.close()
    return total_championships

def get_last_game_date(leagueId: int):
    """
    Get the date of the last game played in a league.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT date FROM fixtures WHERE league_id = ? ORDER BY date DESC LIMIT 1", (leagueId,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    return None

def get_last_seasons_retirements(leagueId: int):
    """
    Get the retirements from the last season of a league.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT last_season_retirements FROM leagues WHERE id = ?", (leagueId,))
    rows = cur.fetchone()
    conn.close()
    # convert the JSON string to a list of dictionaries
    return json.loads(rows[0]) if rows and rows[0] else []