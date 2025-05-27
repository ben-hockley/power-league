from repositories.database import get_db_connection
from repositories.league_repository import get_league_year, get_league_status
from avatars import random_football_avatar
from data.names import get_random_fname, get_random_lname
import random
import os

def add_player_to_depth_chart(teamId: int, playerId: int):
    """
    Add a player to the depth chart for a specific team and position.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    # Get the player's position
    cur.execute("SELECT position FROM players WHERE id = ?", (playerId,))
    row = cur.fetchone()[0]
    if row:
        position = row.lower()
        col_name = f"depth_{position}"
        # Get the current depth chart for the position
        cur.execute(f"SELECT {col_name} FROM teams WHERE id = ?", (teamId,))
        depth_chart_string = str(cur.fetchone()[0])
        # Add the player ID to the depth chart string
        if depth_chart_string:
            depth_chart_string += f",{playerId}"
        else:
            depth_chart_string = str(playerId)
        # Update the depth chart in the database
        cur.execute(f"UPDATE teams SET {col_name} = ? WHERE id = ?", (depth_chart_string, teamId))
        conn.commit()
    conn.close()

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

    # Get the league ID for the team
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT league_id FROM teams WHERE id = ?", (teamId,))
    league_id = cur.fetchone()[0]
    conn.close()

    f_name = get_random_fname()
    l_name = get_random_lname()
    age = random.randint(21, 35)
    draft_year = 2024 - age + 21
    draft_pick = random.randint(1, 200)
    skill = random.randint(1,10) + random.randint(0, 2) * (min(age, 26) - 21)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO players (f_name, l_name, age, draft_year, draft_pick, skill, position, team_id, league_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (f_name, l_name, age, draft_year, draft_pick, skill, position, team_id, league_id))
    
    conn.commit()
    # Update the depth chart for the position
    depth_chart_string = get_depth_chart_string(teamId, position)
    if depth_chart_string is not None and cur.lastrowid is not None:
        depth_chart_string += f",{cur.lastrowid}"
    else:
        depth_chart_string = str(cur.lastrowid)
    
    # generate the player's avatar
    random_football_avatar(cur.lastrowid)

    conn.close()
    save_depth_chart(teamId, position, depth_chart_string)

def create_player(teamId: int, age: int, draft_year: int, skill: int, position: str):
    """
    Create a new player in the database.
    """
    f_name = get_random_fname()
    l_name = get_random_lname()
    draft_pick = None
    conn = get_db_connection()
    # Get the league ID for the team
    cur = conn.cursor()
    cur.execute("SELECT league_id FROM teams WHERE id = ?", (teamId,))
    league_id = cur.fetchone()[0]

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO players (f_name, l_name, age, draft_year, draft_pick, skill, position, team_id, league_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (f_name, l_name, age, draft_year, draft_pick, skill, position, teamId, league_id))
    
    conn.commit()
    random_football_avatar(cur.lastrowid)  # Generate avatar for the player
    conn.close()

def fill_new_team(teamId: int):
    """
    Fill a new team with random players.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT league_id FROM teams WHERE id = ?", (teamId,))
    league_id = cur.fetchone()[0]
    conn.close()

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

    # create some free agents to add to the league
    for i in range(5):
        create_free_agent_player(league_id)
    
    # add 6 new rookies to the next draft class.
    league_status = get_league_status(league_id)
    if league_status == 1: # if the league is active, add rookies to the draft class
        for i in range(6):
            add_rookie_to_draft_class(league_id)

    # Sort all depth charts after filling the team
    clean_all_depth_charts(teamId)
    sort_all_depth_charts(teamId)

def add_rookie_to_draft_class(league_id: int):
    league_year = get_league_year(league_id)
    f_name = get_random_fname()
    l_name = get_random_lname()
    age = 21
    draft_year = league_year
    draft_pick = None # Not drafted yet
    skill = random.randint(1, 10)
    position = random.choice(["QB", "RB","RB", "WR","WR","WR", "OL","OL","OL","OL","OL", "DL","DL","DL","DL", "LB","LB","LB", "DB","DB","DB","DB"])
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO players (f_name, l_name, age, draft_year, draft_pick, skill, position, team_id, league_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (f_name, l_name, age, draft_year, draft_pick, skill, position, 0, league_id))
    conn.commit()
    random_football_avatar(cur.lastrowid)  # Generate avatar for the player
    conn.close()

def create_free_agent_player(leagueId: int):
    """
    Create a new free agent player in the database.
    """
    league_year = get_league_year(leagueId)
    f_name = get_random_fname()
    l_name = get_random_lname()
    draft_year = league_year - random.randint(0, 15)
    age = league_year - draft_year + 21
    draft_pick = None
    skill = random.randint(1, 10)
    position = random.choice(["QB", "RB","RB", "WR","WR","WR", "OL","OL","OL","OL","OL", "DL","DL","DL","DL", "LB","LB","LB", "DB","DB","DB","DB"])

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO players (f_name, l_name, age, draft_year, draft_pick, skill, position, team_id, league_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (f_name, l_name, age, draft_year, draft_pick, skill, position, 0, leagueId))
    
    conn.commit()
    random_football_avatar(cur.lastrowid)  # Generate avatar for the player
    conn.close()

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

# function that ages all players in a league by 1 year, and increases/decreases their skill based on their age
# for example, if a player is under 26, their skill increases by between 0 and 2 (growth stage)
# if a player is over 30, their skill decreases by between 0 and 2 (decline stage)
# if a player is between 26 and 30, their skill increases by between -1 and 1 (prime stage)
def age_league_players(leagueId: int):
    """
    Age all players in the league by 1 year.
    """
     # get the league year
    league_year = get_league_year(leagueId)
    last_year = league_year - 1

    # get all the non rookie free agents in the league
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE league_id = ? AND team_id = 0 AND draft_year != ?", (leagueId, last_year))
    rows = cur.fetchall()
    for player in rows:
        player_id = player[0]
        age = player[3]
        skill = player[6]
        if age is None or skill is None: # skip these players, shouldnt be in the final version
            continue
        # if the player is under 26, increase their skill by between 0 and 3
        elif age < 26:
            skill += random.randint(0, 3)
            # if the player is over 30, decrease their skill by between 0 and 2
        elif age > 30:
            skill -= random.randint(0, 2)
            # if the player is between 26 and 30, increase their skill by between -1 and 2
        else:
            skill += random.randint(-1, 2)

        # age the player by 1 year
        age += 1

        skill = max(1, skill)  # Ensure skill doesn't go below 1
        skill = min(20, skill)

        # update the player's skill and age in the database
        cur.execute("UPDATE players SET age = ?, skill = ? WHERE id = ?", (age, skill, player_id))
        conn.commit()
        if age >= 34 and random.random() > 0.5:
            # delete the player from the database
            cur.execute("DELETE FROM players WHERE id = ?", (player_id,))
            conn.commit()
            # delete the player's avatar from the avatars folder
            try:
                os.remove(f"static/avatars/{player_id}.svg")
            except FileNotFoundError:
                pass
        



    cur.execute("SELECT ID FROM teams WHERE league_id = ?", (leagueId,))
    rows = cur.fetchall()


    teams_ids = [row[0] for row in rows]
    for team_id in teams_ids:
        cur.execute("SELECT * FROM players WHERE team_id = ? AND draft_year != ?", (team_id, last_year))
        players = cur.fetchall()
        for player in players:
            player_id = player[0]
            age = player[3]
            skill = player[6]
            if age is None or skill is None: # skip these players, shouldnt be in the final version
                continue
            # if the player is under 26, increase their skill by between 0 and 2
            elif age < 26:
                skill += random.randint(0, 3)
                # if the player is over 30, decrease their skill by between 0 and 2
            elif age > 30:
                skill -= random.randint(0, 2)
                # if the player is between 26 and 30, increase their skill by between -1 and 1
            else:
                skill += random.randint(-1, 2)

            # age the player by 1 year
            age += 1

            skill = max(1, skill)  # Ensure skill doesn't go below 1
            skill = min(20, skill)  # Ensure skill doesn't go above 20

            # update the player's skill and age in the database
            cur.execute("UPDATE players SET age = ?, skill = ? WHERE id = ?", (age, skill, player_id))
            conn.commit()

            # if a player is 34 or older, 50% chance of retiring
            if age >= 34 and random.random() > 0.5:
                # remove the player from the team
                cur.execute("UPDATE players SET team_id = 0, league_id = 0 WHERE id = ?", (player_id,))
                conn.commit()
                # remove the player from the depth chart
                position = get_player_by_id(player_id)[7]
                depth_chart_string = get_depth_chart_string(team_id, position)
                if depth_chart_string is not None:
                    depth_chart_list = depth_chart_string.split(",")
                    depth_chart_list.remove(str(player_id))
                    new_depth_chart_string = ",".join(depth_chart_list)
                    save_depth_chart(team_id, position, new_depth_chart_string)
                # delete the player from the database
                cur.execute("DELETE FROM players WHERE id = ?", (player_id,))
                conn.commit()
                # delete the player's avatar from the avatars folder
                try:
                    os.remove(f"static/avatars/{player_id}.svg")
                except FileNotFoundError:
                    pass
    #conn.close()

    # following retirements, if any team has under the minimum number of players at any position, add 1 skill rookies to their team.
    # get the league year
    league_year = get_league_year(leagueId)
    last_year = league_year - 1
    
    for team_id in teams_ids:
        cur.execute("SELECT * FROM players WHERE team_id = ? AND draft_year != ?", (team_id, last_year))
        players = cur.fetchall()
        # check if the team has at least 2 QBs, 4 RBs, 5 WRs, 8 OLs, 6 DLs, 5 LBs, and 6 DBs
        num_qbs = len([p for p in players if p[7] == "QB"])
        num_rbs = len([p for p in players if p[7] == "RB"])
        num_wrs = len([p for p in players if p[7] == "WR"])
        num_ols = len([p for p in players if p[7] == "OL"])
        num_dls = len([p for p in players if p[7] == "DL"])
        num_lbs = len([p for p in players if p[7] == "LB"])
        num_dbs = len([p for p in players if p[7] == "DB"])

        if num_qbs < 2:
            create_player(team_id, 21, last_year, random.randint(1, 3), "QB")
        if num_rbs < 3:
            create_player(team_id, 21, last_year, random.randint(1, 3), "RB")
        if num_wrs < 4:
            create_player(team_id, 21, last_year, random.randint(1, 3), "WR")
        if num_ols < 6:
            create_player(team_id, 21, last_year, random.randint(1, 3), "OL")
        if num_dls < 5:
            create_player(team_id, 21, last_year, random.randint(1, 3), "DL")
        if num_lbs < 4:
            create_player(team_id, 21, last_year, random.randint(1, 3), "LB")
        if num_dbs < 5:
            create_player(team_id, 21, last_year, random.randint(1, 3), "DB")
    conn.close()

def create_draft_class(league_id: int):
    """
    Create a draft class for the given league.
    Inserts 6x the number of teams in the league as new players, all aged 21, draft_year 2025,
    team_id 0, and random skill between 1 and 10. Positions are assigned proportionally:
    - 1/22 QB, 2/22 RB, 3/22 WR, 5/22 OL, 4/22 DL, 3/22 LB, 4/22 DB
    """

    # Proportional lineup spots (sum to 22)
    position_weights = [
        ("QB", 1),
        ("RB", 2),
        ("WR", 3),
        ("OL", 5),
        ("DL", 4),
        ("LB", 3),
        ("DB", 4)
    ]
    positions = []
    for pos, count in position_weights:
        positions.extend([pos] * count)
    # positions is now a list of 22 items, e.g. ["QB", "RB", "RB", "WR", "WR", "WR", ...]

    conn = get_db_connection()
    cur = conn.cursor()
    # Get number of teams in league
    cur.execute("SELECT COUNT(*) FROM teams WHERE league_id = ?", (league_id,))
    num_teams = cur.fetchone()[0]
    num_players = num_teams * 6

    league_year = get_league_year(league_id)

    for _ in range(num_players):
        f_name = get_random_fname()
        l_name = get_random_lname()
        age = 21
        draft_year = league_year
        draft_pick = None  # Not drafted yet
        skill = random.randint(1, 10)
        position = random.choice(positions)
        team_id = 0  # Free agent/draft pool

        cur.execute(
            "INSERT INTO players (f_name, l_name, age, draft_year, draft_pick, skill, position, team_id, league_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f_name, l_name, age, draft_year, draft_pick, skill, position, team_id, league_id)
        )
        random_football_avatar(cur.lastrowid)  # Generate avatar for the player
    conn.commit()
    conn.close()

def get_draft_class(league_id: int, league_year: int):
    """
    Get the draft class for the given league.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE draft_year = ? AND league_id = ? ORDER BY skill DESC", (league_year, league_id))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_player_ids():
    """
    Get all player IDs from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM players")
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]

def get_free_agents(league_id: int):
    """
    Get all free agents in the league (remove rookies who are still in college)
    """
    league_year = get_league_year(league_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM players WHERE team_id = 0 AND league_id = ? AND draft_year != ?",
        (league_id, league_year)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

def cut_player(player_id: int):
    """
    Cut a player from the team.
    """
    conn = get_db_connection()
    cur = conn.cursor()

    # remove the player from the depth chart
    position = get_player_by_id(player_id)[7]
    team_id = get_player_by_id(player_id)[8]
    depth_chart_string = get_depth_chart_string(team_id, position)
    if depth_chart_string is not None:
        depth_chart_list = depth_chart_string.split(",")
        depth_chart_list.remove(str(player_id))
        new_depth_chart_string = ",".join(depth_chart_list)
        save_depth_chart(team_id, position, new_depth_chart_string)

    conn.commit()
    # update the player's team_id to 0 (free agent)
    cur.execute("UPDATE players SET team_id = 0 WHERE id = ?", (player_id,))
    conn.commit()

    conn.close()

def sign_player(player_id: int, team_id: int):
    """
    Sign a player to a team. (From free agency)
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE players SET team_id = ? WHERE id = ?", (team_id, player_id))
    conn.commit()
    # add the player to the depth chart
    add_player_to_depth_chart(team_id, player_id)
    conn.close()

def delete_player(player_id: int):
    """
    Delete a player from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM players WHERE id = ?", (player_id,))
    conn.commit()
    conn.close()
    # delete the players avatar from the avatars folder
    os.remove(f"static/avatars/{player_id}.svg")

def get_star_players(team_id: int):
    """
    Return the three highest rated players from a team.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE team_id = ? ORDER BY skill DESC LIMIT 3", (team_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def get_all_players_by_league(league_id: int):
    """
    Get all players in a league.
    """
    league_year = get_league_year(league_id)
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE league_id = ? AND draft_year != ?", (league_id, league_year))
    rows = cur.fetchall()
    conn.close()
    return rows