"""Demo Flask app working utilizing Docker to spawn environments for offensive
security practice."""

import subprocess
import re
import uuid
import os
import functools
from urllib.parse import urlparse

from flask import Flask, render_template, request
from apscheduler.schedulers.background import BackgroundScheduler

import db

PROCESS_TIMEOUT = 30
DB_FILE = "database.db"
MAX_SINGLE_ENVS = 10  # maximum amount of single-container environments
MAX_MULTI_ENVS = 5  # maximum amount of multi-container environments

if not os.path.isfile(DB_FILE):
    print(f"{DB_FILE} not found, initializing a new database")
    db_conn = db.get_connection(DB_FILE)
    db.init(db_conn)
    db_conn.close()


app = Flask(__name__)


def cleanup():
    """This function is called every minute to shut down expired environments"""

    conn = db.get_connection(DB_FILE)

    # clean up multi-container environments
    for env_id, env_dir, prefix in db.get_expired_multi(conn):
        print(
            f"Cleaning up multi-container env: id={env_id}, dir={env_dir}, prefix={prefix}"
        )
        subprocess.run(
            ["docker", "compose", "-p", prefix, "down"],
            timeout=PROCESS_TIMEOUT,
            cwd=env_dir,
        )
        db.del_multi(conn, env_id)

    # clean up single-container environments
    for env_id, container_id in db.get_expired_single(conn):
        print(
            f"Cleaning up single-container env: id={env_id}, container_id={container_id}"
        )
        subprocess.run(
            ["docker", "stop", container_id], timeout=PROCESS_TIMEOUT
        )
        db.del_single(conn, env_id)

    conn.commit()
    conn.close()


# schedule cleanup() to run every minute
scheduler = BackgroundScheduler()
scheduler.add_job(func=cleanup, trigger="interval", seconds=60)
scheduler.start()

def docker_get_port(container_id):
    """Uses the docker command to get the external port for a container

    We rely on it being randomly assigned so we can run multiple containers
    and have each use a different port."""

    # get the random port assigned to the container
    port_process = subprocess.run(
        ["docker", "port", container_id],
        check=True,
        capture_output=True,
        text=True,
        timeout=PROCESS_TIMEOUT,
    )
    # we may get a line for IPv4 and IPv6, we only need one of them
    first_line = port_process.stdout.partition('\n')[0]
    # match everything after the last :
    result = re.search("^.*:(.*)$", first_line)
    port = result.group(1)

    return port

def check_single(func):
    """Decorator to prevent creating a single-container environment if
    MAX_DOCKER_ENVS is exceeded"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = db.get_connection(DB_FILE)
        count = db.get_single_count(conn)
        conn.close()

        if count >= MAX_SINGLE_ENVS:
            print("Too many single-container environments running")
            return render_template("toomany.html")

        return func(*args, **kwargs)

    return wrapper


def check_multi(func):
    """Decorator to prevent creating a multi-container environment if
    MAX_COMPOSE_ENVS is exceeded"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = db.get_connection(DB_FILE)
        count = db.get_multi_count(conn)
        conn.close()

        if count >= MAX_MULTI_ENVS:
            print("Too many multi-container environments running")
            return render_template("toomany.html")

        return func(*args, **kwargs)

    return wrapper


@app.route("/")
def index():
    """An index page showing the available challenges"""

    return render_template("index.html")


@app.route("/status")
def status():
    """A page showing what environments are active"""

    conn = db.get_connection(DB_FILE)
    single_envs = db.get_single_status(conn)
    print(single_envs)
    multi_envs = db.get_multi_status(conn)
    print(multi_envs)
    conn.close()
    return render_template(
        "status.html", single_envs=single_envs, multi_envs=multi_envs
    )


@app.route("/challenge1")
def challenge1():
    """A simple challenge endpoint that just uses an HTML"""

    return render_template("challenge1.html")


@app.route("/challenge2")
@check_single
def challenge2():
    """A challenge endpoint that runs a single-container environment"""

    print("Creating a single-container environment for challenge2")
    run_process = subprocess.run(
        ["docker", "run", "--pull", "never", "-d", "-p", "80", "challenge2"],
        check=True,
        capture_output=True,
        text=True,
        timeout=PROCESS_TIMEOUT,
    )
    container_id = run_process.stdout[:12]

    # store info about this environment in the DB
    conn = db.get_connection(DB_FILE)
    db.add_single(conn, container_id, 60)
    conn.commit()
    conn.close()

    # get the random port assigned to the container
    port = docker_get_port(container_id)

    # this template needs our hostname and the port to tell the user where to connect
    hostname = urlparse(request.base_url).hostname
    return render_template("challenge2.html", hostname=hostname, port=port)


@app.route("/challenge3")
@check_multi
def challenge3():
    """A challenge endpoint that runs a multi-container environment"""

    # you can start multiple docker compose envs in the same directory by using
    # a unique prefix for each
    prefix = uuid.uuid4().hex[:12]
    # this is where our docker-compose.yml file is
    local_dir = "challenges/3"
    # bring the whole thing up
    subprocess.run(
        ["docker", "compose", "-p", prefix, "up", "-d"],
        check=True,
        timeout=PROCESS_TIMEOUT,
        cwd=local_dir,
    )

    # store info about this environment in the DB
    conn = db.get_connection(DB_FILE)
    db.add_multi(conn, local_dir, prefix, 60)
    conn.commit()
    conn.close()

    # figure out what port was allocated to the VPN service
    container_id = prefix + "-vpn-1"
    port = docker_get_port(container_id)

    # grab the generated wireguard config for the client from the container
    # logs (stdout)
    log_process = subprocess.run(
        ["docker", "logs", container_id],
        capture_output=True,
        text=True,
        timeout=PROCESS_TIMEOUT,
    )
    # grab all the lines between <ClientConfig> and </ClientConfig>
    client_config = ""
    in_config = False
    for line in log_process.stdout.splitlines():
        if line == "<ClientConfig>":
            in_config = True
        elif line == "</ClientConfig>":
            break
        elif in_config:
            client_config += line + "\n"
    # add the endpoint on the config
    # (requires a port num and IP which the container doesn't have)
    hostname = urlparse(request.base_url).hostname
    client_config += f"Endpoint = {hostname}:{port}"

    return render_template("challenge3.html", wgconf=client_config)
