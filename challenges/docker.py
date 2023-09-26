"""Functions for running/managing Docker containers"""

import subprocess
import re
import uuid

PROCESS_TIMEOUT = 30


def get_port(container_id):
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
    first_line = port_process.stdout.partition("\n")[0]
    # match everything after the last :
    result = re.search("^.*:(.*)$", first_line)
    port = result.group(1)

    return port


def run_with_port(image, container_port):
    """Starts a single container, returning its port and end_cmd"""

    run_process = subprocess.run(
        ["docker", "run", "--pull", "never", "-d", "-p", str(container_port), image],
        check=True,
        capture_output=True,
        text=True,
        timeout=PROCESS_TIMEOUT,
    )
    container_id = run_process.stdout[:12]

    # get the random port assigned to the container
    port = get_port(container_id)

    end_cmd = f"docker stop {container_id}"

    return (port, end_cmd)


def compose_up_with_vpn(directory, hostname):
    """Runs docker compose up in a particular directory and returns the
    WireGuard config needed to connect to a VPN service in the environment
    and an end_cmd. Hostname is required for the config."""

    # you can start multiple docker compose envs in the same directory by using
    # a unique prefix for each
    prefix = uuid.uuid4().hex[:12]

    # bring the whole thing up
    subprocess.run(
        ["docker", "compose", "-p", prefix, "up", "-d"],
        check=True,
        timeout=PROCESS_TIMEOUT,
        cwd=directory,
    )

    # figure out what port was allocated to the service
    container_id = prefix + "-vpn-1"
    port = get_port(container_id)

    # grab the generated wireguard config for the client from the container
    # logs (stdout)
    log_process = subprocess.run(
        ["docker", "logs", container_id],
        capture_output=True,
        check=True,
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
    client_config += f"Endpoint = {hostname}:{port}"

    end_cmd = f"docker compose -p {prefix} down"

    return (client_config, end_cmd)
