"""A simple challenge endpoint that just uses an HTML template"""

from flask import render_template

# Every challenge needs a unique NAME, FLAG, and DESCRIPTION
NAME         = "Challenge 1"
FLAG         = "piccadilly_circus"
DESCRIPTION  = "Keeping it simple with an in-browser challenge"

def start(conn, user_id, hostname):
    """The start function gets conn, user_id, hostname, and url and should
    return the HTML prompt for the challenge, a command to run to end the
    challenge, and the directory in which to run the command. This function
    must run any containers and do any configuration required."""

    prompt = render_template("challenge1.html")
    end_cmd = None
    cwd = None

    return (prompt, end_cmd, cwd)
