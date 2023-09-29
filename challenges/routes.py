"""Challenge endpoints for starting/stopping/displaying challenges"""

from urllib.parse import urlparse
import subprocess

from flask import Flask, render_template, request, Blueprint, redirect, url_for, abort
from flask_login import login_required, current_user

import db
from challenges import docker
from challenges.decorators import challenge
from challenges.forms import StopChallengeForm

PROCESS_TIMEOUT = 30

challenges_bp = Blueprint(
    "challenges",
    __name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="",
)

@challenges_bp.route("/challenges")
def challenges():
    """An endpoint that shows a user's active challenge or lists available
    challenges if they haven't activated one."""

    conn = db.get_connection()
    prompt = db.get_active_challenge_prompt(conn, current_user.user_id)
    conn.close()

    if prompt:
        return render_template("challenge.html", prompt=prompt)
    return render_template("challenges.html")


@challenges_bp.route("/stop_challenge", methods=['POST'])
@login_required
def stop_challenge():
    """Stops a challenge when passed a url"""

    form = StopChallengeForm()
    if not form.validate():
        abort(400)

    user_id = current_user.user_id
    url = form.url.data
    conn = db.get_connection()
    challenge_row = db.get_challenge(conn, user_id, url) 
    end_cmd = challenge_row['end_cmd']
    cwd = challenge_row['cwd']

    # stop the containers
    if end_cmd:
        subprocess.run(end_cmd, shell=True, cwd=cwd, timeout=PROCESS_TIMEOUT, check=True)

    # remove from the DB
    db.del_challenge(conn, user_id, url)
    conn.commit()
    conn.close()

    return redirect(url_for("challenges.challenges"))


@challenges_bp.route("/challenge1")
@challenge
def challenge1(conn, user_id, hostname, url):
    """A simple challenge endpoint that just uses an HTML template"""

    prompt = render_template("challenge1.html")
    db.add_challenge(conn, user_id, url, prompt)
    return prompt


@challenges_bp.route("/challenge2")
@challenge
def challenge2(conn, user_id, hostname, url):
    """A challenge endpoint that runs a single-container environment"""

    port, end_cmd = docker.run_with_port("challenge2", 80)
    prompt = render_template("challenge2.html", hostname=hostname, port=port)
    db.add_challenge(conn, user_id, url, prompt, end_cmd=end_cmd)
    return prompt


@challenges_bp.route("/challenge3")
@challenge
def challenge3(conn, user_id, hostname, url):
    """A challenge endpoint that runs a multi-container environment that the
    user can VPN into"""

    client_config, end_cmd = docker.compose_up_with_vpn("challenges/3", hostname)
    prompt = render_template("challenge3.html", wgconf=client_config)
    db.add_challenge(
        conn, user_id, url, prompt, end_cmd=end_cmd, cwd="challenges/3"
    )
    return prompt

@challenges_bp.route("/challenge4")
@challenge
def challenge4(conn, user_id, hostname, url):
    """Another simple template challenge"""

    prompt = render_template("challenge4.html")
    db.add_challenge(conn, user_id, url, prompt)
    return prompt

@challenges_bp.route("/challenge5")
@challenge
def challenge5(conn, user_id, hostname, url):
    """Single container challenge involving a .htaccess file"""

    port, end_cmd = docker.run_with_port("challenge5", 80)
    prompt = render_template("challenge5.html", hostname=hostname, port=port)
    db.add_challenge(conn, user_id, url, prompt, end_cmd=end_cmd)
    return prompt
