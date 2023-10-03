"""Challenge endpoints for starting/stopping/displaying challenges"""

from urllib.parse import urlparse
import subprocess

from flask import render_template, request, Blueprint, redirect, url_for, abort
from flask_login import login_required, current_user

import db
from challenges.forms import ChallengeForm

import challenges.challenge1.challenge as challenge1
import challenges.challenge2.challenge as challenge2
import challenges.challenge3.challenge as challenge3
import challenges.challenge4.challenge as challenge4
import challenges.challenge5.challenge as challenge5

AVAILABLE_CHALLENGES = [challenge1, challenge2, challenge3, challenge4, challenge5]

PROCESS_TIMEOUT = 30

challenges_bp = Blueprint(
    "challenges",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/challenges",
)


def stop_challenge(conn, user_id, end_cmd, cwd):
    """Utility function to stop an active challenge and remove it from the DB"""

    if end_cmd:
        subprocess.run(
            end_cmd, shell=True, cwd=cwd, timeout=PROCESS_TIMEOUT, check=True
        )
    db.del_challenge(conn, user_id)
    conn.commit()


@challenges_bp.route("/list_challenges", methods=["GET"])
@login_required
def list_challenges():
    """An endpoint that lists available challenges"""

    chal_list = []
    for index, chal in enumerate(AVAILABLE_CHALLENGES):
        chal_list.append(
            {
                "id": index,
                "name": chal.NAME,
                "description": chal.DESCRIPTION,
            }
        )
    return render_template("list_challenges.html", challenge_list=chal_list)


@challenges_bp.route("/active_challenge", methods=["GET", "POST"])
@login_required
def active_challenge():
    """An endpoint that shows a user's active challenge and accepts POST
    requests to submit a flag or end the challenge."""

    user_id = current_user.user_id

    # check the DB for an active challenge
    conn = db.get_connection()
    challenge_row = db.get_challenge(conn, user_id)

    # make sure they have an active challenge
    if not challenge_row:
        conn.close()
        abort(400)

    name = challenge_row["name"]
    prompt = challenge_row["prompt"]
    flag = challenge_row["flag"]
    end_cmd = challenge_row["end_cmd"]
    cwd = challenge_row["cwd"]

    form = ChallengeForm()
    if form.validate_on_submit():
        if form.capture.data:  # attempt to capture a flag
            if flag == form.flag.data:  # is flag valid?
                # has it not already been captured?
                if not db.get_capture(conn, user_id, name):
                    db.capture_flag(conn, user_id, name)
                    stop_challenge(conn, user_id, end_cmd, cwd)
                    conn.commit()
                    conn.close()
                    current_user.active_challenge = None
                    return render_template("flag_captured.html", name=name)
                form.flag.errors.append("Already captured!")
            else:
                form.flag.errors.append("Flag is incorrect")
        elif form.stop.data:  # stop the active challenge
            stop_challenge(conn, user_id, end_cmd, cwd)
            conn.commit()
            conn.close()
            return redirect(url_for("challenges.list_challenges"))

    conn.close()
    # show the invidual challenge
    return render_template("active_challenge.html", prompt=prompt, form=form)


@login_required
@challenges_bp.route("/start_challenge")
def start_challenge():
    """A route that starts a challenge and redirects to /challenges"""

    user_id = current_user.user_id

    # make sure they specified a valid challenge_id
    challenge_id = request.args.get("id", default=-1, type=int)
    if challenge_id < 0 or challenge_id > len(AVAILABLE_CHALLENGES):
        abort(400)
    challenge = AVAILABLE_CHALLENGES[challenge_id]

    # make sure they don't already have an active challenge
    conn = db.get_connection()
    if db.get_challenge(conn, user_id):
        conn.close()
        abort(403)

    hostname = urlparse(request.base_url).hostname

    # run the start function
    prompt, end_cmd, cwd = challenge.start(conn, user_id, hostname)

    # add the challenge to the DB
    db.add_challenge(
        conn, user_id, challenge.NAME, prompt, end_cmd, cwd, challenge.FLAG
    )
    conn.commit()
    conn.close()

    return redirect(url_for("challenges.active_challenge"))
