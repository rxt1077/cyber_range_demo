import functools

from flask import abort, request, render_template
from flask_login import current_user, login_required
from urllib.parse import urlparse

import db

MAX_CHALLENGES = 1

def challenge(func):
    """Convenience decorator for challenge views.
    * makes a login required
    * checks that the user doesnt have an active challenge
    * passes user_id, conn, and hostname to the function
    * closes and commits the db on exit
    * returns the challenge template rendered with the prompt"""

    @login_required
    @functools.wraps(func)
    def wrapper_challenge():
        user_id = current_user.user_id
        conn = db.get_connection()
        hostname = urlparse(request.base_url).hostname

        # if the user already has a challenge open give an error
        if db.get_challenge_count(conn, user_id) >= MAX_CHALLENGES:
            conn.close()
            abort(403)

        prompt = func(conn, user_id, hostname)

        conn.commit()
        conn.close()

        return render_template("challenge.html", prompt=prompt)
    return wrapper_challenge
