from repositories.database import get_db_connection
from datetime import date, timedelta

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
