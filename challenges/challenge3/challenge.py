"""A simple challenge endpoint that just uses an HTML template"""

from flask import render_template

from challenges import docker

# Every challenge needs a unique NAME, FLAG, and DESCRIPTION
NAME         = "Challenge 3"
FLAG         = "WALLABY"
DESCRIPTION  = "Oh boy, here comes a whole network with multiple hosts"

def start(conn, user_id, hostname):
    """The start function gets conn, user_id, hostname, and url and should
    return the HTML prompt for the challenge, a command to run to end the
    challenge, and the directory in which to run the command. This function
    must run any containers and do any configuration required."""

    cwd = "challenges/challenge3"
    client_config, end_cmd = docker.compose_up_with_vpn(cwd, hostname)
    prompt = render_template("challenge3.html", wgconf=client_config)

    return (prompt, end_cmd, cwd)
