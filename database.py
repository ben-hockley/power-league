import mariadb
from config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME


def get_db_connection():
    """
    Establish a connection to the MariaDB database.
    """
    try:
        connection = mariadb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=3306,
            database=DB_NAME
        )
        return connection
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
        return None
    
def test_db_connection():
    """
    Test the database connection.
    """
    conn = get_db_connection()
    if conn:
        print("Connection successful")
        conn.close()
    else:
        print("Connection failed")

def test_db_cursor(teamId):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM players WHERE team_id = {teamId}")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    conn.close()

#test_db_cursor(myTeamId)

def get_players(teamId):
    """
    Get players from the database for a given team ID.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM players WHERE team_id = {teamId}")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_player_by_id(playerId):
    """
    Get a player from the database by player ID.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM players WHERE id = {playerId}")
    row = cur.fetchone()
    conn.close()
    return row

# depth charts for different positions are recorded in the teams table as a string of comma-separated player IDs (the player IDs referring to records in the players table)
# for example, the depth chart for the QB position of a team might be "1,2,3" where 1 is the starting quarterback, 2 is the backup quarterback, and 3 is the third-string quarterback

def get_depth_chart(player_ids_string):
    """
    Get a depth chart from the database based on player IDs.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    player_ids_string = player_ids_string.strip(",")
    player_ids = [int(x) for x in player_ids_string.split(",")]
    players = []

    for id in player_ids:
        cur.execute(f"SELECT * FROM players WHERE ID = {id}")
        player = cur.fetchone()
        if player:
            players.append(player)
    
    conn.close()
    return players

#depth_chart_string = "1,2,3"
# test the function:
#for player in get_depth_chart(depth_chart_string):
#    print(player)

def get_depth_chart_string(teamId, position):
    conn = get_db_connection()
    cur = conn.cursor()
    position = position.lower()
    col_name = f"depth_{position}"
    cur.execute(f"SELECT {col_name} FROM teams WHERE id = {teamId}")
    row = cur.fetchone()
    conn.close()
    if row:
        depth_chart_string = str(row[0])
        return depth_chart_string
    else:
        return None


def get_depth_chart_by_position(teamId, position):
    """
    Get a depth chart for a specific position for a specific team from the database.
    """
    
    depth_chart_string = get_depth_chart_string(teamId, position)
    if depth_chart_string:
        return get_depth_chart(depth_chart_string)
    else:
        return None
    
# test depth chart by position
# for player in get_depth_chart_by_position(1, "QB"):
#     print(player)

def save_depth_chart(teamId: int, position: str, depth_chart: str):
    """
    Save a depth chart to the database for a specific team and position.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    position = position.lower()
    col_name = f"depth_{position}"
    
    cur.execute(f"UPDATE teams SET {col_name} = ? WHERE id = ?", (depth_chart, teamId))
    conn.commit()
    conn.close()

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