from repositories.database import get_db_connection
import json

def save_game(league_id: int, home_team_id: int, away_team_id: int, details_json: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO games (league_id, home_team_id, away_team_id, date_time, details_json) VALUES (?, ?, ?, NOW(), ?)",
        (league_id, home_team_id, away_team_id, details_json)
    )
    conn.commit()
    game_id = cur.lastrowid
    conn.close()
    return game_id

def get_game_by_id(game_id: int):
    """
    Get a game by ID from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM games WHERE id = ?", (game_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row
    else:
        return None
    
def get_games_by_team_id(team_id: int):
    """
    Get all games for a specific team from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM games WHERE home_team_id = ? OR away_team_id = ?", (team_id, team_id))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_next_fixture(team_id: int):
    """
    Get the next fixture for a specific team from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM fixtures WHERE (home_team_id = ? OR away_team_id = ?) ORDER BY date ASC LIMIT 1",
        (team_id, team_id)
    )
    row = cur.fetchone()
    conn.close()
    if row:
        return row
    else:
        return None

def get_home_score_from_game(game_id: int) -> int:
    """
    Extract the home team's score from the details_json field of a game.
    """

    details_json = get_game_by_id(game_id)[5]
    details = json.loads(details_json)
    return details.get("home_score")

    """
    Get the home score for a specific game.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT home_score FROM games WHERE id = ?", (game_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None