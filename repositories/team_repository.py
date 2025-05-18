from repositories.database import get_db_connection
from repositories.player_repository import fill_new_team

def get_teams_by_user_id(user_id: int):
    """
    Get all teams for a specific user from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM teams WHERE user_id = ?", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_team_by_id(team_id: int):
    """
    Get a team by ID from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM teams WHERE id = ?", (team_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row
    else:
        return None


def get_team_name(team_id: int):
    """
    Get the name of a team by its ID from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT team_name FROM teams WHERE id = ?", (team_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None

def get_team_owner_id(team_id: int):
    """
    Get the owner ID for a specific team from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM teams WHERE id = ?", (team_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None
    
def create_new_team(user_id: int, team_name: str, league_id: int):
    """
    Create a new team in the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO teams (user_id, team_name, league_id) VALUES (?, ?, ?)", (user_id, team_name, league_id))
    conn.commit()
    team_id = cur.lastrowid
    conn.close()
    fill_new_team(team_id)

def get_team_league_id(team_id: int):
    """
    Get the league ID for a specific team from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT league_id FROM teams WHERE id = ?", (team_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None
    
def add_result_to_team(team_id: int, points_for: str, points_against: int):
    """
    Add a result to a team in the database.
    """

    if points_for > points_against:
        result = "W"
    elif points_for < points_against:
        result = "L"
    else:
        result = "T"

    conn = get_db_connection()
    cur = conn.cursor()
    
    if result == "W":
        cur.execute("UPDATE teams SET wins = wins + 1, points_for = points_for + ?, points_against = points_against + ? WHERE id = ?", (points_for, points_against, team_id))
    elif result == "L":
        cur.execute("UPDATE teams SET losses = losses + 1, points_for = points_for + ?, points_against = points_against + ? WHERE id = ?", (points_for, points_against, team_id))
    else: # american football games cant end in a tie, but I haven't applied that to the game engine yet, need to do this.
        cur.execute("UPDATE teams SET points_for = points_for + ?, points_against = points_against + ? WHERE id = ?", (points_for, points_against, team_id))
    conn.commit()
    conn.close()

def get_all_teams():
    """
    Get all teams from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM teams")
    rows = cur.fetchall()
    conn.close()
    return rows