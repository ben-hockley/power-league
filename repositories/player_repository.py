from repositories.database import get_db_connection
from data.names import get_random_fname, get_random_lname
import random

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
    player_ids = player_ids_string.split(",")

    player_ids = [int(x) for x in player_ids if x.isdigit()]
    
    player_ids = [int(x) for x in player_ids]
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

def clean_depth_chart_string(position: str, team_id: int):
    """
    Clean the depth chart string for a specific position for a specific team in the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    position = position.lower()
    col_name = f"depth_{position}"
    
    cur.execute(f"SELECT {col_name} FROM teams WHERE id = ?", (team_id,))
    row = cur.fetchone()
    
    if row:
        depth_chart_string = str(row[0])
        depth_chart_string = depth_chart_string.strip(",")
        depth_chart_string = ",".join(filter(None, depth_chart_string.split(",")))
        cur.execute(f"UPDATE teams SET {col_name} = ? WHERE id = ?", (depth_chart_string, team_id))
        conn.commit()
    
    conn.close()

def clean_all_depth_charts(team_id: int):
    """
    Clean all depth charts for a specific team in the database.
    """
    positions = ["QB", "RB", "WR", "OL", "DL", "LB", "DB"]
    
    for position in positions:
        clean_depth_chart_string(position, team_id)


def sort_depth_chart(team_id: int, position: str):
    """
    Sort the depth chart for a specific position for a specific team in the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    position = position.lower()
    col_name = f"depth_{position}"
    
    cur.execute(f"SELECT {col_name} FROM teams WHERE id = ?", (team_id,))
    row = cur.fetchone()
    
    if row:
        depth_chart_string = str(row[0])
        depth_chart_list = depth_chart_string.split(",")
        depth_chart_list.sort()
        sorted_depth_chart_string = ",".join(depth_chart_list)
        
        cur.execute(f"UPDATE teams SET {col_name} = ? WHERE id = ?", (sorted_depth_chart_string, team_id))
        conn.commit()
    
    conn.close()

def sort_all_depth_charts(team_id: int):
    """
    Sort all depth charts for a specific team in the database.
    """
    positions = ["QB", "RB", "WR", "OL", "DL", "LB", "DB"]
    
    for position in positions:
        sort_depth_chart(team_id, position)

def create_random_player(teamId: int, position: str):
    """
    Create a new player in the database.
    """

    team_id = teamId
    f_name = get_random_fname()
    l_name = get_random_lname()
    age = random.randint(20, 35)
    draft_year = 2025 - age + 20 + random.randint(0, 5)
    draft_pick = random.randint(1, 200)
    skill = random.randint(3,15)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO players (f_name, l_name, age, draft_year, draft_pick, skill, position, team_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (f_name, l_name, age, draft_year, draft_pick, skill, position, team_id))
    
    conn.commit()
    # Update the depth chart for the position
    depth_chart_string = get_depth_chart_string(teamId, position)
    if depth_chart_string is not None and cur.lastrowid is not None:
        depth_chart_string += f",{cur.lastrowid}"
    else:
        depth_chart_string = str(cur.lastrowid)

    conn.close()
    save_depth_chart(teamId, position, depth_chart_string)

def fill_new_team(teamId: int):
    """
    Fill a new team with random players.
    """
    create_random_player(teamId, "QB")
    create_random_player(teamId, "QB")

    create_random_player(teamId, "RB")
    create_random_player(teamId, "RB")
    create_random_player(teamId, "RB")
    create_random_player(teamId, "RB")

    create_random_player(teamId, "WR")
    create_random_player(teamId, "WR")
    create_random_player(teamId, "WR")
    create_random_player(teamId, "WR")
    create_random_player(teamId, "WR")

    create_random_player(teamId, "OL")
    create_random_player(teamId, "OL")
    create_random_player(teamId, "OL")
    create_random_player(teamId, "OL")
    create_random_player(teamId, "OL")
    create_random_player(teamId, "OL")
    create_random_player(teamId, "OL")

    create_random_player(teamId, "DL")
    create_random_player(teamId, "DL")
    create_random_player(teamId, "DL")
    create_random_player(teamId, "DL")
    create_random_player(teamId, "DL")
    create_random_player(teamId, "DL")

    create_random_player(teamId, "LB")
    create_random_player(teamId, "LB")
    create_random_player(teamId, "LB")
    create_random_player(teamId, "LB")
    create_random_player(teamId, "LB")

    create_random_player(teamId, "DB")
    create_random_player(teamId, "DB")
    create_random_player(teamId, "DB")
    create_random_player(teamId, "DB")
    create_random_player(teamId, "DB")
    create_random_player(teamId, "DB")

    # Sort all depth charts after filling the team
    clean_all_depth_charts(teamId)
    sort_all_depth_charts(teamId)

def get_players_by_team(teamId: int):
    """
    Get players from the database for a given team ID.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM players WHERE team_id = {teamId}")
    rows = cur.fetchall()
    conn.close()
    return rows