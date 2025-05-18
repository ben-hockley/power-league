from repositories.database import get_db_connection

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