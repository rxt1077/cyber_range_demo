"""A challenge endpoint that uses a single Docker container"""

from flask import render_template

from challenges import docker

# Every challenge needs a unique NAME, FLAG, and DESCRIPTION
NAME         = "Challenge 2"
FLAG         = "DirBusted"
DESCRIPTION  = "We're running a containerized webserver for this one"

def start(conn, user_id, hostname):
    """The start function gets conn, user_id, hostname, and url and should
    return the HTML prompt for the challenge, a command to run to end the
    challenge, and the directory in which to run the command. This function
    must run any containers and do any configuration required."""

    port, end_cmd = docker.run_with_port("challenge2", 80)
    prompt = render_template("challenge2.html", hostname=hostname, port=port)
    cwd = None

    return (prompt, end_cmd, cwd)
