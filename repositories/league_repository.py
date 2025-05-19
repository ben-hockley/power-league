from repositories.database import get_db_connection

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