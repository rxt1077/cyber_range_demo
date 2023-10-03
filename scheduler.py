"""The scheduler functions are used to perform maintenance tasks at regular
intervals"""

import subprocess

import db

PROCESS_TIMEOUT = 30

def cleanup():
    """This function is called every minute to clean up users that need to be
    logged out. It also stops their challenge if they have one."""

    conn = db.get_connection()

    for user in db.get_expired_users(conn):
        user_id = user["id"]
        db.clear_auto_logout(conn, user_id)
        challenge_row = db.get_challenge(conn, user_id)
        if challenge_row:
            end_cmd = challenge_row['end_cmd']
            cwd = challenge_row['cwd']
            if end_cmd:
                subprocess.run(end_cmd, shell=True, cwd=cwd, timeout=PROCESS_TIMEOUT, check=True)
            db.del_challenge(conn, user_id)
        conn.commit()
    conn.close()
