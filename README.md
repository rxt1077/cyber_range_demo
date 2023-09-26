# Cyber Range Demo

## User environment

Make sure this is run as a non-root user with access to Docker (in the docker group).
Your environment will need SECRET_KEY defined for signing session cookies.
You can put it in a `.env` file and generate it via `python -c 'import secrets; print(secrets.token_hex())'`
You environment will also need a DEFAULT_ADMIN_PASSWORD set.

## Python packages

Python packages for this demo can be installed with `pip install -r requirements.txt`.
I'd recommend using a virtual environment.

## Database

An sqlite3 database stored in database.db is used.
If the file doesn't exist a new database will be created with the correct schema.

## Images

A few Docker images are used in this demo.
Since they are supposed to be built locally they are configured to never be pulled.
This configuration is either in the `subprocess.run` parameters or in the `docker-compose.yml` file.
There's a helper script to build the images: `build_images.sh`.

When the server starts it's expected that these images are built and locally available.
They can be rebuilt at any time and new environments will use the updated images.

## Running via the Flask development server

`flask run`

## Running via gunicorn

`gunicorn -w 1 -b 0.0.0.0 'server:app'`
