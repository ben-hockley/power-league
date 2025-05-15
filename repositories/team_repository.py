from repositories.database import get_db_connection

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
    conn.close()