"""Database functions"""

import sqlite3

DB_FILE = "database.db"


def get_connection():
    """Gets a connection to the database stored in db_name"""

    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.set_trace_callback(print)
    return conn


def init(conn):
    """Initializes a database, dropping previous tables if they exist"""

    cur = conn.cursor()

    cur.executescript(
        """
        DROP TABLE IF EXISTS challenges;

        CREATE TABLE challenges (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          user_id INTEGER UNIQUE NOT NULL,
          name TEXT,
          prompt TEXT NOT NULL,
          end_cmd TEXT,
          cwd TEXT,
          flag TEXT,
          FOREIGN KEY(user_id) REFERENCES users(id)
        );

        DROP TABLE IF EXISTS users;

        CREATE TABLE users (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT UNIQUE NOT NULL,
          password TEXT NOT NULL,
          role INTEGER NOT NULL DEFAULT 0,
          auto_logout_time TIMESTAMP DEFAULT NULL
        );

        DROP TABLE IF EXISTS captures;

        CREATE TABLE captures (
          user_id INTEGER NOT NULL,
          name TEXT,
          PRIMARY KEY (user_id, name)
          FOREIGN KEY(user_id) REFERENCES users(id)
        );

    """
    )


def add_challenge(conn, user_id, name, prompt, end_cmd, cwd, flag):
    """Adds an active challenge to the challenges table"""

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO challenges (user_id, name, prompt, end_cmd, cwd, flag) VALUES (?, ?, ?, ?, ?, ?);",
        (user_id, name, prompt, end_cmd, cwd, flag),
    )


def del_challenge(conn, user_id):
    """Deletes the active challenge based on user_id"""

    cur = conn.cursor()
    cur.execute("DELETE FROM challenges WHERE user_id=?;", (user_id,))


def get_challenge(conn, user_id):
    """Gets the active challenge based on user_id"""
    
    cur = conn.cursor()
    res = cur.execute("SELECT * FROM challenges WHERE user_id=?;", (user_id,))
    return res.fetchone()


def add_user(conn, name, password, role):
    """Adds a user to the user table"""

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, password, role) VALUES (?, ?, ?);",
        (name, password, role),
    )


def del_user(conn, user_id):
    """Deletes a user from the user table"""

    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id=?;", (user_id,))


def get_user(conn, user_id):
    """Retrieves a user by their id"""

    cur = conn.cursor()

    res = cur.execute(
        """
        SELECT id, name, role,
        CAST(((JULIANDAY(auto_logout_time)-JULIANDAY('now')) * 24 * 60) AS INTEGER)
        AS time_remaining
        FROM users
        WHERE id=?;
    """,
        (user_id,),
    )
    return res.fetchone()


def get_all_users(conn):
    """Retrieves information about all users for manage users endpoint"""

    cur = conn.cursor()

    res = cur.execute(
        """
        SELECT id, name, role,
        CAST(((JULIANDAY(auto_logout_time)-JULIANDAY('now')) * 24 * 60) AS INTEGER)
        AS time_remaining
        FROM users;
    """
    )
    return res.fetchall()


def get_user_by_name(conn, name):
    """Retrieves a user by their username"""

    cur = conn.cursor()

    res = cur.execute(
        "SELECT id, name, password, role FROM users WHERE name=?;", (name,)
    )
    return res.fetchone()


def update_user(conn, user_id, name, role):
    """Updates everything _except_ the password of a user"""

    cur = conn.cursor()

    cur.execute("UPDATE users SET name=?, role=? WHERE id=?;",
                (name, role, user_id))

def update_user_password(conn, user_id, password):
    """Updates the password field of a user"""

    cur = conn.cursor()

    cur.execute("UPDATE users SET password=? WHERE id=?;", (password, user_id))


def set_auto_logout(conn, user_id, duration):
    """Sets a user's automatic logout time"""

    cur = conn.cursor()

    cur.execute(
        """
        UPDATE users
        SET auto_logout_time=DATETIME('now', ? || ' minutes')
        WHERE id=?;""",
        (duration, user_id),
    )


def clear_auto_logout(conn, user_id):
    """Sets a user's automatic logout time to NULL"""

    cur = conn.cursor()

    cur.execute("UPDATE users SET auto_logout_time=NULL WHERE id=?;", (user_id,))


def get_expired_users(conn):
    """Gets a list of users who are past their auto logout time"""

    cur = conn.cursor()

    res = cur.execute(
        "SELECT id FROM users WHERE auto_logout_time < CURRENT_TIMESTAMP;"
    )
    return res.fetchall()

def get_capture(conn, user_id, name):
    """Returns a capture row if a challenge has already been completed by a user"""

    cur = conn.cursor()

    res = cur.execute("SELECT * FROM captures WHERE user_id=? AND name=?;", (user_id, name))
    return res.fetchone()

def capture_flag(conn, user_id, name):
    """Adds a captured flag to the captures table"""

    cur = conn.cursor()

    cur.execute("INSERT INTO captures (user_id, name) VALUES (?, ?);", (user_id, name))

def get_leaderboard(conn):
    """Gets the data needed to make a leaderboard display"""

    cur = conn.cursor()

    res = cur.execute("""
        SELECT users.name, GROUP_CONCAT(captures.name, ', ') AS captured, COUNT(user_id) AS total
        FROM captures, users
        WHERE user_id=users.id
        GROUP BY user_id
        ORDER BY total DESC;
        """)

    return res.fetchall()
