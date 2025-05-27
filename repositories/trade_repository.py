from repositories.database import get_db_connection
from repositories.team_repository import get_team_by_id
from repositories.player_repository import get_player_by_id, cut_player, sign_player

def save_trade(proposing_team_id: int, receiving_team_id: int, players_offered: str, players_requested: str):
    """
    Save a trade proposal to the database.
    
    :param proposing_team_id: ID of the team proposing the trade
    :param receiving_team_id: ID of the team receiving the trade proposal
    :param players_offered: Comma-separated string of players ids of players offered by the proposing team
    :param players_requested: Comma-separated string of players ids of players requested by the proposing team
    """
    conn = get_db_connection()
    cur= conn.cursor()
    
    cur.execute(
        "INSERT INTO trades (proposing_team_id, receiving_team_id, players_offered, players_requested) "
        "VALUES (?, ?, ?, ?)",
        (proposing_team_id, receiving_team_id, players_offered, players_requested)
    )
    
    conn.commit()
    conn.close()

def get_trades_proposed(team_id: int):
    """
    Retrieve all trade proposals made by a specific team.
    
    :param team_id: ID of the team whose trade proposals are to be retrieved
    :return: List of trade proposals made by the team
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT * FROM trades WHERE proposing_team_id = ?",
        (team_id,)
    )
    trades = cur.fetchall()
    conn.close()

    trades_details = []

    for trade in trades:
        proposing_team = get_team_by_id(trade[1])
        receiving_team = get_team_by_id(trade[2])
        # Players offered logic
        players_offered = [get_player_by_id(int(pid)) for pid in trade[3].split(',')] if trade[3] else []
        # Players requested logic
        players_requested = [get_player_by_id(int(pid)) for pid in trade[4].split(',')] if trade[4] else []

        trades_details.append({
            "id": trade[0],
            "proposing_team_id": trade[1],
            "proposing_team_name": proposing_team[1] if proposing_team else "",
            "receiving_team_id": trade[2],
            "receiving_team_name": receiving_team[1] if receiving_team else "",
            "players_offered": players_offered,
            "players_requested": players_requested,
        })

    return trades_details

def get_trades_received(team_id: int):
    """
    Retrieve all trade proposals received by a specific team.
    
    :param team_id: ID of the team whose received trade proposals are to be retrieved
    :return: List of trade proposals received by the team
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(
        "SELECT * FROM trades WHERE receiving_team_id = ?",
        (team_id,)
    )
    
    trades = cur.fetchall()
    conn.close()

    trades_details = []

    for trade in trades:
        proposing_team = get_team_by_id(trade[1])
        receiving_team = get_team_by_id(trade[2])
        # Players offered logic
        players_offered = [get_player_by_id(int(pid)) for pid in trade[3].split(',')] if trade[3] else []
        # Players requested logic
        players_requested = [get_player_by_id(int(pid)) for pid in trade[4].split(',')] if trade[4] else []

        trades_details.append({
            "id": trade[0],
            "proposing_team_id": trade[1],
            "proposing_team_name": proposing_team[1] if proposing_team else "",
            "receiving_team_id": trade[2],
            "receiving_team_name": receiving_team[1] if receiving_team else "",
            "players_offered": players_offered,
            "players_requested": players_requested,
        })

    return trades_details

def delete_trade(trade_id: int):
    """
    Delete a trade proposal from the database.
    
    :param trade_id: ID of the trade proposal to be deleted
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(
        "DELETE FROM trades WHERE id = ?",
        (trade_id,)
    )
    
    conn.commit()
    conn.close()

def accept_trade(trade_id: int):
    """
    Accept a trade proposal, updating the teams and players involved.
    
    :param trade_id: ID of the trade proposal to be accepted
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Fetch the trade details
    cur.execute("SELECT * FROM trades WHERE id = ?", (trade_id,))
    trade = cur.fetchone()
    
    if not trade:
        conn.close()
        return "Trade not found."

    proposing_team_id = trade[1]
    receiving_team_id = trade[2]
    players_offered = trade[3].split(',') if trade[3] else []
    players_requested = trade[4].split(',') if trade[4] else []

    # Process players offered
    for pid in players_offered:
        cut_player(int(pid))
        sign_player(int(pid), receiving_team_id)
    
    # Process players requested
    for pid in players_requested:
        cut_player(int(pid))
        sign_player(int(pid), proposing_team_id)

    # Delete the trade after acceptance
    delete_trade(trade_id)

    conn.commit()
    conn.close()
    
    return "Trade accepted successfully."