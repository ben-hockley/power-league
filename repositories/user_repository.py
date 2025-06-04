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

def get_user_by_id(user_id: int):
    """
    Get a user by ID from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row
    else:
        return None

def create_user(username: str, password: str, avatar: str):
    """
    Create a new user in the database.
    """

    # hash the password
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, password, avatar) VALUES (?, ?, ?)", (username, password, avatar))
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
        if isinstance(hashed_password, str):
            hashed_password = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    else:
        return False

def get_user_id(username: str):
    """
    Get the user ID for a specific username from the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()
    if row:
        return row[0]
    else:
        return None