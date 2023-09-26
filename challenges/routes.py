"""Challenge endpoints for starting/stopping/displaying challenges"""

from urllib.parse import urlparse

from flask import Flask, render_template, request, Blueprint, redirect, url_for, abort
from flask_login import login_required, current_user

import db
from challenges import docker

MAX_CHALLENGES = 1

challenges_bp = Blueprint(
    "challenges",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="",
)


@challenges_bp.route("/challenges")
@login_required
def challenges():
    """An endpoint that shows a user's active challenge or lists available
    challenges if they haven't activated one."""

    conn = db.get_connection()
    prompt = db.get_active_challenge_prompt(conn, current_user.user_id)
    conn.close()

    if prompt:
        return render_template("challenge.html", prompt=prompt)
    return render_template("challenges.html")


@challenges_bp.route("/stop_challenge", methods=["POST"])
@login_required
def stop_challenge():
    """Stops a challenge when passed a url"""

    user_id = current_user.user_id
    url = request.form.get("url")

    conn = db.get_connection()
    db.del_challenge(conn, user_id, url)
    conn.commit()
    conn.close()

    return redirect(url_for("challenges.challenges"))


@challenges_bp.route("/challenge1")
@login_required
def challenge1():
    """A simple challenge endpoint that just uses an HTML template"""

    user_id = current_user.user_id

    conn = db.get_connection()

    # if the user already has a challenge open give an error
    if db.get_challenge_count(conn, user_id) >= MAX_CHALLENGES:
        conn.close()
        abort(403)

    url = "/challenge1"
    prompt = render_template("challenge1.html")

    db.add_challenge(conn, user_id, url, prompt)
    conn.commit()
    conn.close()

    return render_template("challenge.html", prompt=prompt)


@challenges_bp.route("/challenge2")
@login_required
def challenge2():
    """A challenge endpoint that runs a single-container environment"""

    user_id = current_user.user_id

    conn = db.get_connection()

    # if the user already has a challenge open give an error
    if db.get_challenge_count(conn, user_id) >= MAX_CHALLENGES:
        conn.close()
        abort(403)

    print("Creating a single-container environment for challenge2")
    port, end_cmd = docker.run_with_port("challenge2", 80)

    # this template needs our hostname and the port to tell the user where to connect
    hostname = urlparse(request.base_url).hostname
    prompt = render_template("challenge2.html", hostname=hostname, port=port)

    db.add_challenge(conn, user_id, "/challenge2", prompt, end_cmd)
    conn.commit()
    conn.close()

    return render_template("challenge.html", prompt=prompt)


@challenges_bp.route("/challenge3")
@login_required
def challenge3():
    """A challenge endpoint that runs a multi-container environment that the
    user can VPN into"""

    user_id = current_user.user_id

    conn = db.get_connection()

    # if the user already has a challenge open give an error
    if db.get_challenge_count(conn, user_id) >= MAX_CHALLENGES:
        conn.close()
        abort(403)

    hostname = urlparse(request.base_url).hostname
    client_config, end_cmd = docker.compose_up_with_vpn("challenges/3", hostname)
    prompt = render_template("challenge3.html", wgconf=client_config)

    db.add_challenge(
        conn, user_id, "/challenge3", prompt, end_cmd=end_cmd, cwd="challenges/3"
    )
    conn.commit()
    conn.close()

    return render_template("challenge.html", prompt=prompt)
