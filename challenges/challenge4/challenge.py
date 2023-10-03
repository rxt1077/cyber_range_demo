"""Another simple template challenge"""

from flask import render_template

# Every challenge needs a unique NAME, FLAG, and DESCRIPTION
NAME         = "Challenge 4"
FLAG         = "DomoArigatoMrRoboto"
DESCRIPTION  = "Another HTML/JS challenge"

def start(conn, user_id, hostname):
    """The start function gets conn, user_id, hostname, and url and should
    return the HTML prompt for the challenge, a command to run to end the
    challenge, and the directory in which to run the command. This function
    must run any containers and do any configuration required."""

    prompt = render_template("challenge4.html")
    end_cmd = None
    cwd = None

    return (prompt, end_cmd, cwd)
