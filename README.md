# Cyber Range Demo

## Python Packages

Python packages for this demo can be installed with `pip -r requirements.txt`.
I'd recommend using a virtual environment.

## Database

An sqlite3 database stored in database.db is used.
If the file doesn't exist a new database will be created with the correct schema.

## Images

A few Docker images are used in this demo.
They can be built and tagged with:

* `cd challenges/2; docker build -t challenge2 .`
* `cd challenges/3/wg_vpn; docker build -t wg_vpn .`
* `cd challenges/3/dr_sneaky; docker build -t dr_sneaky .`

It is expected that these images are built and locally available.
They can be rebuilt at any time and new environments will make use of the updated images

## Flask App

To run the development server: `flask --app server.py run`
