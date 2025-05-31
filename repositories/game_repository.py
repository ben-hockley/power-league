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
    
def get_record_last_5_games(team_id: int):
    """
    Get the record of the last 5 games for a specific team from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM games WHERE home_team_id = ? OR away_team_id = ? ORDER BY date_time DESC LIMIT 5",
        (team_id, team_id)
    )
    rows = cur.fetchall()
    conn.close()

    record = []
    
    if rows:
        for row in rows:
            game_details = json.loads(row[5])
            if row[2] == team_id: # if home team
                result = 'W' if game_details['home_score'] > row['away_score'] else 'L' if row['home_score'] < row['away_score'] else 'D'
            else: # if away team
                result = 'A' if row['home_score'] > row['away_score'] else 'H' if row['home_score'] < row['away_score'] else 'D'
            record.append(result)