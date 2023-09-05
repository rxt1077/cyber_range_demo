"""Database functions"""

import sqlite3


def get_connection(db_name):
    """Gets a connection to the database stored in db_name"""

    conn = sqlite3.connect(db_name)
    conn.set_trace_callback(print)
    return conn


def init(conn):
    """Initializes a database, dropping previous tables if they exist"""

    cur = conn.cursor()

    cur.executescript(
        """
        DROP TABLE IF EXISTS single_envs;

        CREATE TABLE single_envs (
          id           INTEGER PRIMARY KEY AUTOINCREMENT,
          container_id TEXT NOT NULL,
          start_time   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          end_time     TIMESTAMP NOT NULL
        );

        DROP TABLE IF EXISTS multi_envs;

        CREATE TABLE multi_envs ( 
          id         INTEGER PRIMARY KEY AUTOINCREMENT,
          dir        TEXT NOT NULL,
          prefix     TEXT NOT NULL,
          start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
          end_time   TIMESTAMP NOT NULL
        );
    """
    )


def add_multi(conn, directory, prefix, duration):
    """Adds a multi-container environment to the multi_envs table"""

    cur = conn.cursor()

    # https://stackoverflow.com/questions/62911225/query-parameter-binding-in-datetime-function-of-sqlite3
    cur.execute(
        """
        INSERT INTO multi_envs (dir, prefix, end_time)
        VALUES (?, ?, DATETIME('now', ? || ' minutes'));
        """,
        (directory, prefix, duration),
    )


def get_expired_multi(conn):
    """Returns a list of all multi-container environments that have expired"""

    cur = conn.cursor()

    res = cur.execute(
        "SELECT id, dir, prefix FROM multi_envs WHERE end_time < CURRENT_TIMESTAMP;"
    )
    return res.fetchall()


def del_multi(conn, env_id):
    """Removes a multi-container environment from the multi_envs table"""

    cur = conn.cursor()

    cur.execute("DELETE FROM multi_envs WHERE id=?;", (env_id,))


def add_single(conn, container_id, duration):
    """Adds a single-container environment"""

    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO single_envs (container_id, end_time)
        VALUES (?, DATETIME('now', ? || ' minutes'));
        """,
        (container_id, duration),
    )


def get_expired_single(conn):
    """Returns a list of all single-container environments that have expired"""

    cur = conn.cursor()

    res = cur.execute(
        "SELECT id, container_id FROM single_envs WHERE end_time < CURRENT_TIMESTAMP;"
    )
    return res.fetchall()


def del_single(conn, env_id):
    """Removes a single-container environment from the docker_envs table"""

    cur = conn.cursor()

    cur.execute("DELETE FROM single_envs WHERE id=?;", (env_id,))


def get_single_count(conn):
    """Returns a count of how many single-container environments are running"""

    cur = conn.cursor()

    res = cur.execute("SELECT COUNT(id) FROM single_envs;")
    return res.fetchone()[0]


def get_multi_count(conn):
    """Returns a count of how many multi-container environments are running"""

    cur = conn.cursor()

    res = cur.execute("SELECT COUNT(id) FROM multi_envs;")
    return res.fetchone()[0]


def get_single_status(conn):
    """Returns the rows of the single_envs table"""

    cur = conn.cursor()

    res = cur.execute("SELECT * FROM single_envs;")
    return res.fetchall()


def get_multi_status(conn):
    """Returns the rows of the single_envs table"""

    cur = conn.cursor()

    res = cur.execute("SELECT * FROM multi_envs;")
    return res.fetchall()
