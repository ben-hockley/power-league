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