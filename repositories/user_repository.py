from repositories.database import get_db_connection
import bcrypt

def get_user_by_username(username: str):
    """
    Get a user by username from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row
    else:
        return None

def create_user(username: str, password: str):
    """
    Create a new user in the database.
    """

    # hash the password
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def check_password(username: str, password: str):
    """
    Check if the password is correct for a specific user.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        hashed_password = row[0]
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    else:
        return False
